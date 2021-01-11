# -*- coding: utf-8 -*-
from collections import OrderedDict

import http
import logging
import os
import pathlib
import requests
import shutil
from artifactory import ArtifactoryPath

from crosspm.helpers.config import CROSSPM_DEPENDENCY_FILENAME, CROSSPM_DEPENDENCY_LOCK_FILENAME, Config  # noqa
from crosspm.helpers.content import DependenciesContent
from crosspm.helpers.exceptions import *
from crosspm.helpers.package import Package
from crosspm.helpers.parser import Parser
from crosspm.output_formatters.deps_txt_lock_list_formatter import DepsTxtLockListFormatter


class Command(object):
    def entrypoint(self, *args, **kwargs):
        assert NotImplemented


class Downloader(Command):
    def __init__(self, config, do_load, recursive, parser_class=Parser):
        self._log = logging.getLogger('crosspm')
        self._config = config  # type: Config
        self.cache = config.cache
        self.solid = config.solid
        self.common_parser = parser_class('common', {}, config)
        self._root_package = Package('<root>', 0, None, {self._config.name_column: '<root>'}, self, None,
                                     self.common_parser)
        self.recursive = recursive

        if not config.deps_path:
            config.deps_path = \
                config.deps_file_name if config.deps_file_name else CROSSPM_DEPENDENCY_FILENAME
        deps_path = config.deps_path
        if deps_path.__class__ is DependenciesContent:
            # HACK
            pass
            self._deps_path = deps_path
        else:
            deps_path = config.deps_path.strip().strip('"').strip("'")
            self._deps_path = os.path.realpath(os.path.expanduser(deps_path))

        if not config.depslock_path:
            config.depslock_path = \
                config.deps_lock_file_name if config.deps_lock_file_name else CROSSPM_DEPENDENCY_LOCK_FILENAME
        depslock_path = config.depslock_path
        if depslock_path.__class__ is DependenciesContent:
            # HACK
            self._depslock_path = depslock_path
        else:
            depslock_path = depslock_path.strip().strip('"').strip("'")
            self._depslock_path = os.path.realpath(os.path.expanduser(depslock_path))

        self.do_load = do_load

    def update_progress(self, msg, progress):
        self._log.info('\r{0} [{1:10}] {2}%'.format(msg, '#' * int(float(progress) / 10.0), int(progress)))

    # Get list of all packages needed to resolve all the dependencies.
    # List of Package class instances.
    def get_dependency_packages(self, list_or_file_path=None, property_validate=True):
        """
        :param list_or_file_path:
        :param property_validate: for `root` packages we need check property, bad if we find packages from `lock` file,
        we can skip validate part
        """
        if list_or_file_path is None:
            list_or_file_path = self._depslock_path
            if not os.path.isfile(list_or_file_path):
                list_or_file_path = self._deps_path

        _packages = OrderedDict()
        if isinstance(list_or_file_path, str):
            self._log.info('Reading dependencies ... [%s]', list_or_file_path)
        for i, _src in enumerate(self._config.sources()):
            if i > 0:
                self._log.info('')
                self._log.info('Next source ...')
            _found_packages = _src.get_packages(self, list_or_file_path, property_validate)
            _packages.update(
                OrderedDict([(k, v) for k, v in _found_packages.items() if _packages.get(k, None) is None]))
            if not self._config.no_fails:
                if isinstance(list_or_file_path, (list, tuple)):
                    list_or_file_path = [x for x in list_or_file_path if
                                         _packages.get(x[self._config.name_column], None) is None]
                elif isinstance(list_or_file_path, dict) and isinstance(list_or_file_path.get('raw', None), list):
                    list_or_file_path['raw'] = [x for x in list_or_file_path['raw'] if
                                                _packages.get(x[self._config.name_column], None) is None]

        return _packages

    def get_usedby_packages(self, list_or_file_path=None, property_validate=True):
        """

        :param list_or_file_path:
        :param property_validate: for `root` packages we need check property, bad if we find packages from `lock` file,
        we can skip validate part
        :return:
        """
        if list_or_file_path is None:
            list_or_file_path = self._depslock_path
            if not os.path.isfile(list_or_file_path):
                list_or_file_path = self._deps_path

        _packages = OrderedDict()
        if isinstance(list_or_file_path, str):
            self._log.info('Reading dependencies ... [%s]', list_or_file_path)
        for i, _src in enumerate(self._config.sources()):
            if i > 0:
                self._log.info('')
                self._log.info('Next source ...')
            _found_packages = _src.get_usedby(self, list_or_file_path, property_validate)
            _packages.update(
                OrderedDict([(k, v) for k, v in _found_packages.items() if _packages.get(k, None) is None]))
            if not self._config.no_fails:
                if isinstance(list_or_file_path, (list, tuple)):
                    list_or_file_path = [x for x in list_or_file_path if
                                         _packages.get(x[self._config.name_column], None) is None]
                elif isinstance(list_or_file_path, dict) and isinstance(list_or_file_path.get('raw', None), list):
                    list_or_file_path['raw'] = [x for x in list_or_file_path['raw'] if
                                                _packages.get(x[self._config.name_column], None) is None]

        return _packages

    def find_package_in_artifactory(self, package):
        return

    # Download packages or just unpack already loaded (it's up to adapter to decide)
    def download_packages(self):
        with open(self._config.depslock_path) as f:
            packages_path_in_repo = DepsTxtLockListFormatter.read_packages_from_lock_file(f)

        session = requests.Session()

        packages_not_found = []

        output_path = self._config.output_path

        if output_path is not None and output_path != '':
            pathlib.Path(output_path).mkdir(parents=True, exist_ok=True)

        for package_path in packages_path_in_repo:

            errors = {}
            package_download_done = False

            for src in self._config.sources():
                if package_download_done:
                    break

                session.auth = src.get_auth_params().auth
                packages = src.generate_full_urls_from_package_path_in_repo(package_path)

                # packages = self.find_package_in_artifactory(src, package)
                for p in packages:
                    try:
                        ap = ArtifactoryPath(p, session=session)
                        dst_path = os.path.join(output_path, ap.name)

                        with ap.open() as input, open(dst_path, "wb") as output:
                            shutil.copyfileobj(input, output)

                        package_download_done = True

                        self._log.info(f"Success {ap} downloaded to {dst_path}")

                        break

                    except RuntimeError as e:
                        if isinstance(e.args[0], int):
                            errors[ap] = http.HTTPStatus(e.args[0])
                        else:
                            errors[ap] = e

            if not package_download_done:
                packages_not_found += [package_path]
                self._log.error(f"PACKAGE NOT FOUND {package_path}. Errors for attempts {errors}")

        if packages_not_found:
            raise CrosspmException(CROSSPM_ERRORCODE_PACKAGE_NOT_FOUND,
                                   'Some package(s) not found: {}'.format(', '.join(packages_not_found)))

    def entrypoint(self, *args, **kwargs):
        self.download_packages(*args, **kwargs)

    def search_dependencies(self, depslock_file_path, deps_content=None):
        self._log.info('Check dependencies ...')
        self._root_package.find_dependencies(depslock_file_path, property_validate=True, deps_content=deps_content, )
        self._log.info('')
        self.check_not_found()

    def check_not_found(self):
        _not_found = self.get_not_found_packages()
        if _not_found:
            raise CrosspmException(
                CROSSPM_ERRORCODE_PACKAGE_NOT_FOUND,
                'Some package(s) not found: {}'.format(', '.join(_not_found))
            )

    def get_not_found_packages(self):
        return self._root_package.get_none_packages()

    def add_package(self, pkg_name, package):
        _added = False
        if package is not None:
            _added = True
        return _added, package

    def get_raw_packages(self):
        """
        Get all packages
        :return: list of all packages
        """
        return self._root_package.all_packages

    def get_tree_packages(self):
        """
        Get all packages, with hierarchy
        :return: list of first level packages, with child
        """
        return self._root_package.packages

    def iter_packages_params(self, list_or_file_path, deps_content=None):
        return self.common_parser.iter_packages_params(list_or_file_path, deps_content)
