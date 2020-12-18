from tabulate import tabulate

class DepsTxtLockListFormatter:
    def __init__(self):
        pass

    @staticmethod
    def write_packages_to_lock_file(deps_lock_file_path, packages):

        packages_for_table = [[p.art_package.name, p.art_package.version, p.art_package.art_path.path_in_repo] for p in packages.values()]
        table = tabulate(packages_for_table, headers=[], tablefmt='plain')

        with open(deps_lock_file_path, 'w+') as f:
           f.write(table)

        #
        # with open(deps_lock_file_path, 'w+') as f:
        #     for p in packages.values():
        #         print(f"{p.art_package.name}    {p.art_package.}p.art_package.art_path.path_in_repo, file=f)

    @staticmethod
    def read_packages_from_lock_file(deps_lock_file_path):

        paths = []

        with open(deps_lock_file_path) as f:
            for l in f.read.splitlines():
                p = l.split()
                if p.len != 2:
                    raise Exception(f"Line invalid:\n{l}\nExpect format of line as:\n<name> <version> <path>")
                paths.append(l.split()[2])

