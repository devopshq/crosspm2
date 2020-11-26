
class PackageMatch:
    def __init__(self, line):
        placeholders = line.split()

        placeholders_count = len(placeholders)

        if placeholders_count not in [2, 3]:
            raise line

        self.package_name = placeholders[0]
        self.version_pattern = placeholders[1]

        if placeholders_count == 3:
            self.contracts = placeholders[2]
        else:
            self.contracts = []

    def is_package_fullname_match_version_pattern(self, package):
        return package.name == self.package_name and fnmatch.fnmatch(package.fullversion, self.version_pattern)

    def is_package_contracts_match(self, package):
        return all(package.has_contract(c) for c in self.contracts)

    def is_package_match(self, package):
        return self.is_package_fullname_match_version_pattern(package) and self.is_package_contracts_match(package)


# package version

class DepsTxtSimpleParser:
    def __init__(self, deps_txt):

        for line in deps_txt:
            p = line.split()
            PackagePattern(p)name = p[0]
            version_pattern = p[1]
            contracts = p[2]



