# -*- coding: utf-8 -*-
from addict import Dict
from pathlib import PurePath

from crosspm.contracts.package_version import PackageVersion
from crosspm.deps_txt_parsers.deps_simple import PackageMatch
from crosspm.package_parsers.debian_package_name_parser import DebianPackageNameParser


class Parser2():
    def __init__(self, name, data, config):
        # super().__init__(name, data, config)
        self._name = 'repo2'
        self._rules = {}
        self._rules['path'] = ['{server}/{repo}/**/{package}_{version}.deb']

    def iter_packages_params(self, list_or_file_path, deps_content=None):
        with open(list_or_file_path, 'r', encoding="utf-8-sig") as f:
            for i, line in enumerate(f):
                line = line.strip()

                #  if i == 0 and line.startswith(''.join(map(chr,(1087,187,1111)))):
                if i == 0 and line.startswith(chr(1087) + chr(187) + chr(1111)):  # TODO: why?
                    line = line[3:]

                if not line or line.startswith(('#', '[',)):
                    continue

                pm = PackageMatch(line)
                res = {'package': pm.package_name, 'version': pm.version_pattern, 'contracts': pm.contracts,
                       'server': None, 'repo': None}
                yield res

    def get_vars(self):
        return ['server', 'repo', 'package', 'version']

    def validate_path(self, path, params):
        p = PurePath(path)
        debian_package = DebianPackageNameParser.parse_from_package_name(p.name)
        package_version = PackageVersion(debian_package.fullversion)

        res_params = Dict()
        res_params.update(params)
        res_params.version = package_version.release

        res_params_raw = Dict()
        res_params_raw.version = debian_package.fullversion

        return True, res_params, res_params_raw

    def merge_with_mask(self, column, value):
        return value

    @staticmethod
    def split_fixed_pattern_with_file_name(path):
        """
        Split path into fixed, masked parts and filename
        :param path: e.g
https://repo.example.com/artifactory/libs-cpp-release.snapshot/boost/1.60-pm/*.*.*/vc110/x86/win/boost.*.*.*.tar.gz
        :return:
            _path_fixed: https://repo.example.com/artifactory/libs-cpp-release.snapshot/boost/1.60-pm/
            _path_pattern: *.*.*/vc100/x86/win
            _file_name_pattern: boost.*.*.*.tar.gz
        """
        _first_pattern_pos = path.find('*')
        _path_separator_pos = path.rfind('/', 0, _first_pattern_pos)
        _path_fixed = path[:_path_separator_pos]
        _path_pattern = path[_path_separator_pos + 1:]
        _file_name_pattern_separator_pos = _path_pattern.rfind('/', 0)
        _file_name_pattern = _path_pattern[_file_name_pattern_separator_pos + 1:]

        if _path_pattern.find('*') == -1 or _file_name_pattern_separator_pos == -1:
            _path_pattern = ""
        else:
            _path_pattern = _path_pattern[:_file_name_pattern_separator_pos]

        return _path_fixed, _path_pattern, _file_name_pattern
