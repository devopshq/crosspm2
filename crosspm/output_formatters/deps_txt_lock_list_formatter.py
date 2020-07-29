class DepsTxtLockListFormatter:
    def __init__(self):
        pass

    @staticmethod
    def write_packages_to_lock_file(deps_lock_file_path, packages):

        with open(deps_lock_file_path, 'w+') as f:
            for p in packages.values():
                print(p.art_package.art_path.path_in_repo, file=f)

    @staticmethod
    def read_packages_from_lock_file(deps_lock_file_path):

        with open(deps_lock_file_path) as f:
            return f.read().splitlines()
