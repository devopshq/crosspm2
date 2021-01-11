from tabulate import tabulate


class DepsTxtLockListFormatter:
    def __init__(self):
        pass

    @staticmethod
    def write_packages_to_lock_file(deps_lock_stream, packages):

        packages_for_table = [[p.art_package.name, p.art_package.version, p.art_package.art_path.path_in_repo] for p in
                              packages.values()]
        table = tabulate(packages_for_table, headers=[], tablefmt='plain')

        deps_lock_stream.write(table)

    @staticmethod
    def read_packages_from_lock_file(deps_lock_stream):

        paths = []

        for i, line in enumerate(deps_lock_stream.read().splitlines(), 1):
            sline = line.strip()
            if not sline or sline.startswith('#'):
                continue

            p = sline.split()
            if len(p) != 3:
                raise Exception(
                    f"Line {i} invalid, expect 3 columns"
                    ", but has {len(p)}:\n<<<{line}>>>\nsplitted into: {p}\n"
                    "Expect format of line as:\n<name> <version> <path>")
            paths.append(p[2])

        return paths
