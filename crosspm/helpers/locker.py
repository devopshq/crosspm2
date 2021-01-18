from crosspm.helpers.downloader import Downloader
from crosspm.helpers.parser import Parser


class Locker(Downloader):
    def __init__(self, config, do_load, recursive, parser_cls=Parser):
        # TODO: revise logic to allow recursive search without downloading
        super(Locker, self).__init__(config, do_load, recursive, parser_cls)

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
            # raise CrosspmException(
            #     CROSSPM_ERRORCODE_WRONG_ARGS,
            #     'Dependencies and Lock files are same: "{}".'.format(deps_file_path),
            # )

        if packages is None:
            self.search_dependencies(deps_file_path)
        else:
            self._root_package.packages = packages

        self._log.info('Writing lock file [{}]'.format(depslock_file_path))

        # output_params = {
        #     'out_format': 'lock',
        #     'output': depslock_file_path,
        # }
        # Output(config=self._config).write_output(output_params, self._root_package.packages)
        self._log.info('Done!')

    def entrypoint(self, *args, **kwargs):
        self.lock_packages(*args, **kwargs)
