import logging
from ordered_set import OrderedSet

from crosspm.contracts.package import is_packages_contracts_graph_resolvable
from crosspm.helpers.exceptions import CrosspmException, CROSSPM_ERRORCODE_PACKAGE_NOT_FOUND, \
    CrosspmBundleNoValidContractsGraph, CrosspmBundleTriggerPackagesHasNoValidContractsGraph, \
    CrosspmBundleTriggerPackageHidesHigherVersion


class Bundle:
    def __init__(self, deps, packages_repo, trigger_packages, enable_tp_hides_higher_version):
        # it is vital for deps to be list, orderedset (or something with insertion order savings),
        # we need the order of packages in dependencies.txt to take next package
        # when no contracts satisfied
        self._log = logging.getLogger('crosspm')

        self._deps = OrderedSet(deps)
        self._packages_repo = sorted(packages_repo, reverse=True)

        self._trigger_packages = []
        if trigger_packages:
            for tp in trigger_packages:
                self._trigger_packages.append(Bundle.find_trigger_package_in_packages_repo(tp, self._packages_repo))
                if not enable_tp_hides_higher_version:
                    validate_trigger_package_doesnt_hide_higher_version(tp, self._packages_repo)

        self._packages = dict()
        self._bundle_contracts = {}

    @staticmethod
    def find_trigger_package_in_packages_repo(trigger_package, repo_packages):

        for p in repo_packages:
            if p == trigger_package:
                return p

        raise CrosspmException(CROSSPM_ERRORCODE_PACKAGE_NOT_FOUND,
                               f"trigger_package = <{trigger_package}> NOT FOUND in repo_packages : {repo_packages}")

    def calculate(self):

        self._log.info('deps: {}'.format(self._deps))
        self._log.info('trigger_packages: {}'.format(self._trigger_packages))
        self._log.info('packages_repo: {}'.format(self._packages_repo))

        if not is_packages_contracts_graph_resolvable(self._trigger_packages):
            raise CrosspmBundleTriggerPackagesHasNoValidContractsGraph(self._trigger_packages)

        for tp in self._trigger_packages:
            self._packages[tp.name] = tp

        while True:
            rest_packages_to_find = self.rest_packages_to_find(self._deps, self._packages)
            if not rest_packages_to_find:
                break

            self.update_bundle_contracts()
            self.find_next_microservice_package(rest_packages_to_find)

        return self._packages

    def find_next_microservice_package(self, rest_packages_to_find):

        failed_contracts = set()
        microservice_packages = [i for i in self._packages_repo if i.is_microservice(rest_packages_to_find[0])]

        if not microservice_packages:
            raise CrosspmBundleNoValidContractsGraph(f"cant select next package for current contracts:\n"
                                                     f"rest_packages_to_find : {rest_packages_to_find}\n"
                                                     f"bundle.packages : {self._packages}")

        for p in [i for i in self._packages_repo if i.is_microservice(rest_packages_to_find[0])]:
            package = self.is_package_corresponds_bundle_current_contracts(failed_contracts, p, self._bundle_contracts)
            if package:
                self._package_add(package)
                return

        for package_name, package in self._packages.copy().items():
            if package.has_contracts(failed_contracts):
                if package in self._trigger_packages:
                    raise CrosspmBundleNoValidContractsGraph(
                        f"no tree resolve with trigger_packages {self._trigger_packages}, threre is no appropriate packages with specified package contracts")

                del self._packages[package_name]
                self._packages_repo.remove(package)

        return

    def select_next_microservice_package_out_of_current_contracts(self, next_packages_out_of_current_contracts,
                                                                  select_order):
        for i in select_order:
            if i in next_packages_out_of_current_contracts:
                return next_packages_out_of_current_contracts[i]

        return None

    def is_package_corresponds_bundle_current_contracts(self, failed_contracts, package,
                                                        bundle_contracts):

        intersection_package_contracts = package.calc_contracts_intersection(bundle_contracts)

        if not intersection_package_contracts:
            return package

        failed_contracts.update(intersection_package_contracts)
        for c in intersection_package_contracts:

            if package.contracts[c] == bundle_contracts[c]:
                failed_contracts.discard(c)

        if not failed_contracts:
            return package

        return None

    def remove_packages_with_higher_contracts_then(self, package_lowering_contract):

        for p in [*self._packages.values()]:
            if p.is_any_contract_higher(package_lowering_contract):
                if p in self._trigger_packages:
                    raise CrosspmBundleNoValidContractsGraph(
                        f"no tree resolve with trigger_packages {self._trigger_packages}, threre is no appropriate packages with specified package contracts")

                del self._packages[p.name]

    def update_bundle_contracts(self):
        self._bundle_contracts = dict()
        for p in self._packages.values():
            self._bundle_contracts.update(p.contracts)

    def rest_packages_to_find(self, deps, packages):
        return deps - packages.keys()

    def _package_add(self, package):
        self._packages[package.name] = package


def validate_trigger_package_doesnt_hide_higher_version(tp, packages):
    for p in [i for i in packages if i.is_microservice(tp.name)]:
        if tp.version < p.version:
            raise CrosspmBundleTriggerPackageHidesHigherVersion(tp, p)

    return True
