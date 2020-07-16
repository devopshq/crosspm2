# -*- coding: utf-8 -*-
import copy
import json
import logging
import http.client
import os
import time
from collections import OrderedDict
from datetime import datetime

import requests
from artifactory import ArtifactoryPath
from requests.auth import HTTPBasicAuth

from crosspm.adapters import artifactoryaql
from crosspm.contracts.bundle import Bundle
from crosspm.helpers.exceptions import *  # noqa
import crosspm.contracts.package
from crosspm.helpers.package import Package

CHUNK_SIZE = 1024

setup = {
    "name": [
        "jfrog-artifactory-aql2",
    ],
}

session = requests.Session()


class Adapter(artifactoryaql.Adapter):
    def get_packages(self, source, parser, downloader, list_or_file_path, property_validate=True):
        """

        :param source:
        :param parser:
        :param downloader:
        :param list_or_file_path:
        :param property_validate: for `root` packages we need check property, bad if we find packages from `lock` file,
        we can skip validate part
        :return:
        """
        logging.basicConfig(level=logging.DEBUG)
        http.client.HTTPConnection.debuglevel = 1
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

        _art_auth_etc = self.get_auth_params(list_or_file_path, source)

        _pkg_name_column = self._config.name_column
        _secret_variables = self._config.secret_variables
        _packages_found = OrderedDict()
        _packed_exist = False
        _packed_cache_params = None
        self._log.info('parser: {}'.format(parser._name))

        repo_returned_packages_all = []

        for _paths in parser.get_paths(list_or_file_path, source):

            # If "parser"-column specified - find only in this parser
            parser_names = _paths['params'].get('parser')
            if parser_names and parser_names != "*":
                self._log.info("Specified parsers: {}".format(parser_names))
                parsers = parser_names.split(',')
                if parser._name not in parsers:
                    self._log.info("Skip parser: {}".format(parser._name))
                    continue

            _packages = []
            _params_found = {}
            _params_found_raw = {}
            last_error = ''
            _pkg_name = _paths['params'][_pkg_name_column]
            for _sub_paths in _paths['paths']:
                _tmp_params = dict(_paths['params'])
                self._log.info('repo: {}'.format(_sub_paths['repo']))
                for _path in _sub_paths['paths']:
                    _tmp_params['repo'] = _sub_paths['repo']

                    _path_fixed, _path_pattern, _file_name_pattern = parser.split_fixed_pattern_with_file_name(_path)
                    _packages, _package_versions_with_contracts = self.find_package_versions(_art_auth_etc, _file_name_pattern, _packages, _params_found,
                                                           _params_found_raw, _path_pattern, _tmp_params, last_error,
                                                           parser, _paths['params'])

            _package = None

            if _packages:
                repo_returned_packages_all += _package_versions_with_contracts

        # # HACK for not found packages
        # _package_names = [x[self._config.name_column] for x in list_or_file_path['raw']]
        # _packages_found_names = [x.name for x in _packages_found.values()]
        # for package in _package_names:
        #     if package not in _packages_found_names:
        #         _packages_found[package] = None

        package_names = [x[self._config.name_column] for x in list_or_file_path['raw']]

        bundle = Bundle(package_names, repo_returned_packages_all, None)

        bundle_packages = bundle.calculate().values()
        for p in bundle_packages:
            _stat_pkg = self.pkg_stat(p.art_path)
            _packages_found[p.name] = Package(p.name, p.art_path, p.paths_params, downloader, self, parser,
                                p.params, p.params_raw, _stat_pkg)

        for p in package_names:
            if p not in _packages_found.keys():
                _packages_found[package] = None

        return _packages_found

    def parse_contracts_from_artifactory_results(self, properties):
        contracts = dict()

        for p in properties:
            if p['key'].startswith('c.'):
                contracts[p['key']] = p['value'][0]

        return contracts


    def find_package_versions(self, _art_auth_etc, _file_name_pattern, _packages, _params_found, _params_found_raw,
                              _path_pattern, _tmp_params, last_error, parser, paths_params):
        try:
            package_versions_with_contracts = []
            _artifactory_server = _tmp_params['server']
            _search_repo = _tmp_params['repo']

            # Get AQL path pattern, with fixed part path, without artifactory url and repository name
            _aql_path_pattern = ""
            if _path_pattern:
                _aql_path_pattern = _path_pattern

            _aql_query_url = '{}/api/search/aql'.format(_artifactory_server)
            _aql_query_dict = {
                "repo": {
                    "$eq": _search_repo,
                },
                "path": {
                    "$match": _aql_path_pattern,
                },
                "name": {
                    "$match": _file_name_pattern,
                },
            }
            # Remove path if is empty string
            if not _aql_path_pattern:
                _aql_query_dict.pop('path')
            query = 'items.find({query_dict}).include("*", "property")'.format(
                query_dict=json.dumps(_aql_query_dict))
            session.auth = _art_auth_etc['auth']
            r = session.post(_aql_query_url, data=query, verify=_art_auth_etc['verify'])
            r.raise_for_status()

            _found_paths = r.json()
            for _found in _found_paths['results']:
                _repo_path = "{artifactory}/{repo}/{path}/{file_name}".format(
                    artifactory=_artifactory_server,
                    repo=_found['repo'],
                    path=_found['path'],
                    file_name=_found['name'])
                _repo_path = ArtifactoryPath(_repo_path, **_art_auth_etc)

                _mark = 'found'
                _matched, _params, _params_raw = parser.validate_path(str(_repo_path), _tmp_params)
                if _matched:
                    contracts = self.parse_contracts_from_artifactory_results(_found['properties'])

                    package_with_contracts = crosspm.contracts.package.ArtifactoryPackage(_params['package'],
                                                                                          _params_raw['version'],
                                                                                          contracts, _repo_path,
                                                                                          _params, _params_raw,
                                                                                          paths_params
                                                                                          )

                    package_versions_with_contracts.append(package_with_contracts)

                    _params_found[_repo_path] = {k: v for k, v in _params.items()}
                    _params_found_raw[_repo_path] = {k: v for k, v in _params_raw.items()}

                    _mark = 'valid'
                    _packages += [_repo_path]
                    _params_found[_repo_path]['filename'] = str(_repo_path.name)
                    _params_found[_repo_path]['parser'] = parser._name

                self._log.debug('  {}: {}'.format(_mark, str(_repo_path)))
        except RuntimeError as e:
            try:
                err = json.loads(e.args[0])
            except Exception:
                err = {}
            if isinstance(err, dict):
                # Check errors
                # :e.args[0]: {
                #                 "errors" : [ {
                #                     "status" : 404,
                #                     "message" : "Not Found"
                #                  } ]
                #             }
                for error in err.get('errors', []):
                    err_status = error.get('status', -1)
                    err_msg = error.get('message', '')
                    if err_status == 401:
                        msg = 'Authentication error[{}]{}'.format(err_status,
                                                                  (': {}'.format(
                                                                      err_msg)) if err_msg else '')
                    elif err_status == 404:
                        msg = last_error
                    else:
                        msg = 'Error[{}]{}'.format(err_status,
                                                   (': {}'.format(err_msg)) if err_msg else '')
                    if last_error != msg:
                        self._log.error(msg)
                    last_error = msg
        return _packages, package_versions_with_contracts

    def get_auth_params(self, list_or_file_path, source):
        _auth_type = source.args['auth_type'].lower() if 'auth_type' in source.args else 'simple'
        _art_auth_etc = {}
        if 'auth' in source.args:
            self.search_auth(list_or_file_path, source)
            if _auth_type == 'simple':
                _art_auth_etc['auth'] = HTTPBasicAuth(*tuple(source.args['auth']))
                session.auth = _art_auth_etc['auth']
                # elif _auth_type == 'cert':
                #     _art_auth_etc['cert'] = os.path.realpath(os.path.expanduser(source.args['auth']))
        if 'auth' not in _art_auth_etc:
            msg = 'You have to set auth parameter for sources with artifactory-aql adapter'
            # self._log.error(msg)
            raise CrosspmException(
                CROSSPM_ERRORCODE_ADAPTER_ERROR,
                msg
            )
        if 'verify' in source.args:
            _art_auth_etc['verify'] = source.args['verify'].lower in ['true', 'yes', '1']
        else:
            _art_auth_etc['verify'] = False
        return _art_auth_etc