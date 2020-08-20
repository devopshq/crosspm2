# -*- coding: utf-8 -*-
import http.client
import json
import logging
from collections import OrderedDict

import requests
from addict import Dict
from artifactory import ArtifactoryPath

import crosspm.contracts.package
from crosspm.adapters import artifactoryaql
from crosspm.contracts.bundle import Bundle
from crosspm.helpers.exceptions import *  # noqa
from crosspm.helpers.package import Package

PACKAGE_PROPERTY_CONTRACT_PREFFIX = 'c.'
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
        # logging.basicConfig(level=logging.DEBUG)
        # http.client.HTTPConnection.debuglevel = 1
        # requests_log = logging.getLogger("requests.packages.urllib3")
        # requests_log.setLevel(logging.DEBUG)
        # requests_log.propagate = True

        _art_auth_etc = source.get_auth_params()

        _pkg_name_column = self._config.name_column
        _secret_variables = self._config.secret_variables
        _packages_found = OrderedDict()
        _packed_exist = False
        _packed_cache_params = None
        self._log.info('parser: {}'.format(parser._name))

        repo_returned_packages_all = []

        for _path in source.get_paths(list_or_file_path['raw']):

            last_error = ''

            _tmp_params = Dict(_path.params)
            self._log.info('repo: {}'.format(_tmp_params.repo))

            _path_fixed, _path_pattern, _file_name_pattern = parser.split_fixed_pattern_with_file_name(_path.path)
            _package_versions_with_contracts = self.find_package_versions(_art_auth_etc, _file_name_pattern,
                                                                          _path_pattern, _tmp_params,
                                                                          last_error,
                                                                          parser, _tmp_params)

            _package = None

            if _package_versions_with_contracts:
                repo_returned_packages_all += _package_versions_with_contracts

        package_names = [x[self._config.name_column] for x in list_or_file_path['raw']]

        bundle = Bundle(package_names, repo_returned_packages_all, None)

        bundle_packages = bundle.calculate().values()
        for p in bundle_packages:
            _packages_found[p.name] = Package(p.name, p.art_path, p, p.paths_params, downloader, self, parser,
                                              p.params, p.params_raw, p.pkg_stat())

        for p in package_names:
            if p not in _packages_found.keys():
                _packages_found[p.name] = None

        return _packages_found

    def parse_contracts_from_items_find_results(self, properties):
        contracts = Dict()

        for p in properties:
            if p.key.startswith(PACKAGE_PROPERTY_CONTRACT_PREFFIX):
                contracts[p.key] = p.value[0]

        return contracts

    def find_package_versions(self, _art_auth_etc, _file_name_pattern,
                              _path_pattern, _tmp_params, last_error, parser, paths_params):
        try:
            package_versions_with_contracts = []
            _artifactory_server = _tmp_params.server
            _search_repo = _tmp_params.repo

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

            _found_paths = Dict(r.json())
            for _found in _found_paths.results:
                _repo_path = "{artifactory}/{repo}/{path}/{file_name}".format(
                    artifactory=_artifactory_server,
                    repo=_found.repo,
                    path=_found.path,
                    file_name=_found.name)
                _repo_path = ArtifactoryPath(_repo_path, **_art_auth_etc)

                _mark = 'found'
                _matched, _params, _params_raw = parser.validate_path(str(_repo_path), _tmp_params)
                if _matched:
                    contracts = self.parse_contracts_from_items_find_results(_found.properties)

                    package_with_contracts = crosspm.contracts.package.ArtifactoryPackage(_params.package,
                                                                                          _params_raw.version,
                                                                                          contracts, _repo_path,
                                                                                          _params, _params_raw,
                                                                                          paths_params,
                                                                                          _found
                                                                                          )

                    package_versions_with_contracts.append(package_with_contracts)

                    _mark = 'valid'

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
        return package_versions_with_contracts

    # def find_package_in_repo_by_fullname(self, source, package_fullname):
    #
    #     return

    def download_package(self, source, package_fullname, package_local_fullpath):
        packages = self.find_package_versions(self.get_auth(source), package_fullname, '', {}, last_error, self.parser,
                                              {})

        with packages[0].art_path.open() as fd, open(package_local_fullpath, "wb") as out:
            out.write(fd.read())

