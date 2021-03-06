# -*- coding: utf-8 -*-
from crosspm.helpers.locker import Locker

from crosspm.helpers.parser2 import Parser2
from dohq_common.deps_txt.deps_txt_lock_list_formatter import DepsTxtLockListFormatter


class Locker2(Locker):
    def __init__(self, config, do_load, recursive):
        # TODO: revise logic to allow recursive search without downloading
        super(Locker2, self).__init__(config, do_load, recursive, Parser2)

    def lock_packages(self, deps_file_path=None, depslock_file_path=None, packages=None):
        """
        Lock packages. Downloader search packages
        """
        if deps_file_path is None:
            deps_file_path = self._deps_path
        if depslock_file_path is None:
            depslock_file_path = self._depslock_path
        if deps_file_path == depslock_file_path:
            depslock_file_path += '.lock'

        if packages is None:
            self.search_dependencies(deps_file_path)
        else:
            self._root_package.packages = packages

        self._log.info('Writing lock file [{}]'.format(depslock_file_path))

        # DepsTxtLockTableFormatter.write(depslock_file_path, self._root_package.packages)
        with open(depslock_file_path, 'w+') as f:
            DepsTxtLockListFormatter.write_packages_to_lock_file(f, self._root_package.packages)

        self._log.info('Done!')
