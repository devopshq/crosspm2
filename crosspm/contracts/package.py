import dateutil
from addict import Dict

from crosspm.contracts.contract import Contract
from crosspm.contracts.package_version import PackageVersion
from crosspm.package_parsers.debian_package_name_parser import DebianPackageNameParser

PACKAGE_PROPERTY_CONTRACT_PREFFIX = 'contracts.'


class Package:

    def __init__(self, name: str, version: str, contracts: dict):
        self.name = name
        self.version = PackageVersion(version)
        self.contracts = contracts

    def __hash__(self):
        return hash(str(self.name) + str(self.version))

    def __str__(self):
        return "{}.{}({})".format(self.name, self.version, ",".join(str(s[1]) for s in sorted(self.contracts.items())))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.name == other.name and self.version == other.version

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return (self.name, self.version) < (other.name, other.version)

    def is_microservice(self, microservice):
        return self.name == microservice

    def has_contract(self, contract):
        return contract in self.contracts

    def is_contract_lower_then(self, other):
        if other.name in self.contracts:
            return self.contracts[other.name].value < other.value

        raise BaseException("package {} has no contract {}", str(self), str(other))

    def is_contract_higher_then(self, other):
        if other.name in self.contracts:
            return self.contracts[other.name].value > other.value

        raise BaseException("package {} has no contract {}", str(self), str(other))

    def is_any_contract_higher(self, other):
        for c in self.calc_contracts_intersection(other.contracts):
            if self.contracts[c].value > other.contracts[c].value:
                return True

        return False

    def calc_contracts_intersection(self, contracts):
        return self.contracts.keys() & contracts.keys()

    @staticmethod
    def create_contracts(contracts):
        return {c[0]: Contract(c[0], c[1]) for c in contracts}

    @staticmethod
    def create_contracts_from_dict(contracts):
        return {k: Contract(k, v) for k, v in contracts.items()}

    @staticmethod
    def create_package(package):

        if len(package) == 3:
            return Package(package[0], str(package[1]), Package.create_contracts(package[2]))

        return Package(package[0], str(package[1]), Package.create_contracts([]))

    @staticmethod
    def create_package_debian(package_name):

        p = DebianPackageNameParser.parse_from_package_name(package_name)

        return Package.create_package((p.package, p.fullversion))

    @staticmethod
    def create_packages(*packages):
        res = set()
        for p in packages:
            res.add(Package.create_package(p))

        return res


def create_artifactory_package(art_path):
    contracts = parse_contracts_from_package_properties(art_path.properties)
    debian_package = DebianPackageNameParser.parse_from_package_name(art_path.name)

    return ArtifactoryPackage(art_path, debian_package.package, debian_package.fullversion, contracts)


def parse_contracts_from_package_properties(properties):
    contracts = Dict()

    for p in properties:
        if p.startswith(PACKAGE_PROPERTY_CONTRACT_PREFFIX):
            contracts[p] = properties[p]

    return contracts


def is_packages_contracts_graph_resolvable(packages):
    contracts = {}

    for p in packages:
        contracts_intersection = contracts.keys() & p.contracts.keys()
        for c in contracts_intersection:
            if not p.contracts[c] == contracts[c]:
                return False

        contracts.update(p.contracts)

    return True


class ArtifactoryPackage(Package):
    def __init__(self, art_path, name, version, contracts):
        super(ArtifactoryPackage, self).__init__(name, version,
                                                 Package.create_contracts_from_dict(contracts))
        self.art_path = art_path
        self.stat_pkg = None

    def strisodate_to_timestamp(self, date):
        return dateutil.parser.parse(date).timestamp()

    def pkg_stat(self):
        if not self.stat_pkg:
            self.stat = self.art_path.stat()
        return self.stat_pkg
