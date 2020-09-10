from parse import compile

from crosspm.helpers.exceptions import CrosspmException, CROSSPM_ERRORCODE_VERSION_PATTERN_NOT_MATCH

DEBIAN_PACKAGENAME_PATTERN = compile('{}_{}_{}.deb')

# https://www.debian.org/doc/manuals/debian-faq/pkg-basics.en.html
# 7.3. Why are Debian package file names so long?
# The Debian binary package file names conform to the following convention:
# <foo>_<VersionNumber>-<DebianRevisionNumber>_<DebianArchitecture>.deb


class DebianPackageNameParser:

    def __init__(self, package, version, revision, arch):
        self.package = package
        self.version = version
        self.revision = revision
        self.arch = arch

    @classmethod
    def parse_from_package_name(cls, package_name):

        try:
            package, fullversion, arch = DEBIAN_PACKAGENAME_PATTERN.parse(package_name)
            version, sep, revision = fullversion.partition('-')
            return DebianPackageNameParser(package, version, revision, arch)
        except TypeError:
            raise CrosspmException(CROSSPM_ERRORCODE_VERSION_PATTERN_NOT_MATCH, f"package name <{package_name}> mismatch debian name convension pattern <foo>_<Version>_<DebianArchitecture>.deb")


    def __str__(self):
        return self.fullname

    def __repr__(self):
        return str(self)

    @property
    def fullname(self):
        return "{}_{}_{}.deb".format(self.package, self.fullversion, self.arch)

    @property
    def fullversion(self):

        if self.revision:
            return f"{self.version}-{self.revision}"
        return f"{self.version}"
