# -*- coding: utf-8 -*-
from collections import OrderedDict

import json
import packaging
import requests
from addict import Dict
from artifactory import ArtifactoryPath

import crosspm.contracts.package
from crosspm import InvalidPackage
from crosspm.adapters.artifactoryaql import ArtifactoryAql
from crosspm.contracts.bundle import Bundle
from crosspm.helpers.exceptions import *  # noqa
from crosspm.helpers.package import Package

CHUNK_SIZE = 1024

setup = {
    "name": [
        "jfrog-artifactory-aql2",
    ],
}

session = requests.Session()


class ArtifactoryAql2(ArtifactoryAql):
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
        # http.client.HTTPConnection.debuglevel = 1
        # requests_log = logging.getLogger("requests.packages.urllib3")
        # requests_log.setLevel(logging.DEBUG)
        # requests_log.propagate = True

        _art_auth_etc = source.get_auth_params()

        _packages_found = OrderedDict()
        self._log.info('parser: {}'.format(parser._name))

        repo_returned_packages_all = []

        for _path in source.get_paths(list_or_file_path['raw']):

            _tmp_params = Dict(_path.params)
            self._log.info('repo: {}'.format(_tmp_params.repo))

            session.auth = _art_auth_etc['auth']
            aql = ArtifactoryPath(f"{_tmp_params.server}", session=session)

            _path_fixed, _path_pattern, _file_name_pattern = parser.split_fixed_pattern_with_file_name(_path.path)

            _package_versions_with_contracts, packages_with_invalid_naming_convention = \
                self.find_package_versions(_file_name_pattern,
                                           _path_pattern,
                                           aql,
                                           _tmp_params.repo)

            if _package_versions_with_contracts:
                _package_versions_with_all_contracts, package_versions_with_missing_contracts = \
                    remove_package_versions_with_missing_contracts(
                        _package_versions_with_contracts,
                        _path.params['contracts']
                    )

                for p, missing_contracts in package_versions_with_missing_contracts.items():
                    self._log.info(f"Skip {p} - missing contracts {missing_contracts}")

                if _package_versions_with_all_contracts:
                    repo_returned_packages_all += _package_versions_with_all_contracts

        package_names = [x[self._config.name_column] for x in list_or_file_path['raw']]

        bundle = Bundle(package_names, repo_returned_packages_all,
                        downloader._config.trigger_package)

        bundle_packages = bundle.calculate().values()

        self._log.info('Final bundle packages with contracts:')
        print_packages_by_contracts_scheme(self._log, bundle_packages)

        for p in bundle_packages:
            _packages_found[p.name] = Package(p.name, p.art_path, p, {}, downloader, self, parser,
                                              {}, {})

        for p in package_names:
            if p not in _packages_found.keys():
                _packages_found[p.name] = None

        return _packages_found

    def find_package_versions(self, _file_name_pattern,
                              _path_pattern, aql, search_repo):
        try:
            packages_with_invalid_naming_convention = []
            package_versions_with_contracts = []

            query = self.prepare_aql_query(_file_name_pattern, _path_pattern, search_repo)
            artifacts = aql.aql(query)

            for art_path in map(aql.from_aql, artifacts):
                try:

                    package_with_contracts = crosspm.contracts.package.create_artifactory_package(art_path)

                    package_versions_with_contracts.append(package_with_contracts)

                    self._log.debug(f"  valid: {str(art_path)}")

                except packaging.version.InvalidVersion as e:
                    packages_with_invalid_naming_convention.append(InvalidPackage(art_path, e))
                    self._log.warn(f"{e} for {art_path}")

        except RuntimeError as e:
            self.try_parse_http_error(e)

        return package_versions_with_contracts, packages_with_invalid_naming_convention

    def prepare_aql_query(self, _file_name_pattern, _path_pattern, _search_repo):
        # Get AQL path pattern, with fixed part path, without artifactory url and repository name
        _aql_path_pattern = ""
        if _path_pattern:
            _aql_path_pattern = _path_pattern
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
        query = f'items.find({json.dumps(_aql_query_dict)}).include("*", "property")'

        return query

    def try_parse_http_error(self, e):
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

                self._log.error('Error[{}]{}'.format(err_status,
                                                     (': {}'.format(err_msg)) if err_msg else ''))


def print_packages_by_contracts_scheme(logger, packages):
    for p in packages:
        logger.info(f"  {p}")


def remove_package_versions_with_missing_contracts(package_versions, contracts):
    if not contracts:
        return package_versions, {}

    package_versions_with_all_contracts = []
    package_versions_with_missing_contracts = {}

    for p in package_versions:
        package_version_missing_contracts = []
        for c in contracts.strip().split(';'):
            if not p.has_contract(c):
                package_version_missing_contracts += [c]

        if package_version_missing_contracts:
            package_versions_with_missing_contracts[p] = package_version_missing_contracts
        else:
            package_versions_with_all_contracts += [p]

    return package_versions_with_all_contracts, package_versions_with_missing_contracts
