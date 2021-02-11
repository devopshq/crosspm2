import pytest

from crosspm.contracts.bundle import Bundle
from crosspm.contracts.package import Package
from crosspm.helpers.exceptions import CrosspmBundleNoValidContractsGraph, CrosspmException


def create_packages_repo(packages):
    packages_repo = [Package.create_package_from_tuple(p) for p in packages]

    packages_repo.sort(key=lambda p: str(p), reverse=True)

    return packages_repo


def packages_repo_contract_single_value():
    packages =[
        ('db', '1', 'contracts.db=a1'),
        ('db', '2', 'contracts.db=A2'),
        ('db', '3', 'contracts.db=B3'),
        ('db', '4', 'contracts.db=b4'),

        ('be', '1', 'contracts.db=a1;contracts.rest=1'),
        ('be', '2', 'contracts.db=A2;contracts.rest=1'),
        ('be', '3', 'contracts.db=A1;contracts.rest=2'),
        ('be', '4', 'contracts.db=b4;contracts.rest=2'),

        ('ui', '1', 'contracts.rest=1'),
        ('ui', '2', 'contracts.rest=2'),
        ('ui', '3', 'contracts.rest=3'),
        ('ui', '4', 'contracts.rest=4'),

        ('ncp', '1', ''),
        ('ncp', '2', ''),
        ('ncp', '3', ''),
    ]

    return create_packages_repo(packages)

def create_bundle(deps_txt, packages_repo, trigger_packages):
    return Bundle(deps_txt, packages_repo, trigger_packages)


class TestBundle:

    @pytest.mark.parametrize(
        "test_case",
        [
            {
                'trigger_packages': [('db', 4)],
                'packages': [('db', 4), ('ui', 2), ('be', 4), ('ncp', 3)]
            },
            {
                'trigger_packages': [('be', 4)],
                'packages': [('db', 4), ('ui', 2), ('be', 4), ('ncp', 3)]
            },
            {
                'trigger_packages': [('ui', 2)],
                'packages': [('db', 4), ('ui', 2), ('be', 4), ('ncp', 3)]
            },
            {
                'trigger_packages': [('be', 1)],
                'packages': [('db', 1), ('ui', 1), ('be', 1), ('ncp', 3)]
            },
            {
                'trigger_packages': [],
                'packages': [('db', 4), ('ui', 2), ('be', 4), ('ncp', 3)]
            },
            {
                'trigger_packages': [('be', 2), ('db', 2)],
                'packages': [('db', 2), ('ui', 1), ('be', 2), ('ncp', 3)]
            },
        ]
    )
    def test_calculate_success(self, test_case):
        deps_txt = ['db', 'be', 'ui', 'ncp']
        self.do_test_calculate_case(deps_txt, packages_repo_contract_single_value(), test_case)


    @pytest.mark.parametrize(
        "test_case",
        [
            {
                'trigger_packages': [('ui', 4)]
            },
            {
                'trigger_packages': [('be', 1), ('db', 2)],
            },

        ]
    )
    def test_calculate_failure(self, test_case):
        with pytest.raises(CrosspmException) as exc_info:
            deps_txt = ['db', 'be', 'ui', 'ncp']
            self.do_test_calculate_case(deps_txt, packages_repo_contract_single_value(), test_case)


    def do_test_calculate_case(self, deps_txt, packages_repo, test_case) -> None:
        tp = []
        if test_case['trigger_packages']:
            tp = [Package.create_package_from_tuple(tp) for tp in test_case['trigger_packages']]

        bundle = create_bundle(deps_txt, packages_repo, tp)

        packages = set(bundle.calculate().values())

        expected_packages = set()
        for p in Package.create_packages(*test_case['packages']):
            expected_packages.add(packages_repo[packages_repo.index(p)])

        assert packages == expected_packages


    def packages_repo_contract_multiple_values(self):
        packages =[
            ('db', '1', 'contracts.db=90fe'),
            ('db', '2', 'contracts.db=10be'),
            ('db', '3', 'contracts.db=81ab'),
            ('db', '4', 'contracts.db=00fe'),
            ('db', '5', 'contracts.db=00be'),

            ('be', '1', 'contracts.db=81ab;contracts.rest=1'),
            ('be', '2', 'contracts.db=00fe,10be;contracts.rest=1'),
            ('be', '11', 'contracts.db=10be;contracts.rest=1'),

            ('ui', '1', 'contracts.rest=1'),
            ('ui', '2', 'contracts.rest=1'),
            ('ui', '3', 'contracts.rest=3'),
            ('ui', '4', 'contracts.rest=4'),

            ('ncp', '1', ''),
            ('ncp', '2', ''),
            ('ncp', '3', ''),
        ]
        return create_packages_repo(packages)

    @pytest.mark.parametrize(
        "test_case",
        [
            # {
            #     'trigger_packages': [('be', 2)],
            #     'packages': [('db', 2), ('be', 2), ('ui', 2), ('ncp', 3)]
            # },
            {
                'trigger_packages': [],
                'packages': [('db', 4), ('be', 2), ('ui', 2), ('ncp', 3)]
            },
        ]
    )
    def test_contract_multiple_values_calculate_success(self, test_case):
        deps_txt = ['db', 'be', 'ui', 'ncp']
        self.do_test_calculate_case(deps_txt, self.packages_repo_contract_multiple_values(), test_case)
