import pytest

from crosspm.contracts.bundle import Bundle
from crosspm.contracts.package import Package
from crosspm.helpers.exceptions import CrosspmBundleNoValidContractsGraph, CrosspmException


def packages_repo():
    packages =[
        ('db', '1', 'contracts.db=1'),
        ('db', '2', 'contracts.db=2'),
        ('db', '3', 'contracts.db=3'),
        ('db', '4', 'contracts.db=4'),

        ('be', '1', 'contracts.db=1;contracts.rest=1'),
        ('be', '2', 'contracts.db=2;contracts.rest=1'),
        ('be', '3', 'contracts.db=1;contracts.rest=2'),
        ('be', '4', 'contracts.db=4;contracts.rest=2'),

        ('ui', '1', 'contracts.rest=1'),
        ('ui', '2', 'contracts.rest=2'),
        ('ui', '3', 'contracts.rest=3'),
        ('ui', '4', 'contracts.rest=4'),

        ('ncp', '1', ''),
        ('ncp', '2', ''),
        ('ncp', '3', ''),
    ]

    packages_repo = [Package.create_package_from_tuple(p) for p in packages]

    packages_repo.sort(key=lambda p: str(p), reverse=True)

    return packages_repo

def dependencies_txt():
    return ['db', 'be', 'ui', 'ncp']


class TestBundle:

    def create_bundle(self, trigger_packages):
        return Bundle(dependencies_txt(), packages_repo(), trigger_packages)

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
        self.do_test_calculate_case(test_case)


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
            self.do_test_calculate_case(test_case)


    def do_test_calculate_case(self, test_case) -> None:
        tp = []
        if test_case['trigger_packages']:
            tp = [Package.create_package_from_tuple(tp) for tp in test_case['trigger_packages']]

        bundle = self.create_bundle(tp)

        packages = set(bundle.calculate().values())
        expected_packages = set(Package.create_packages(*test_case['packages']))

        assert packages == expected_packages

#
# def test_calculate():
#     assert False
#
#
# def test_find_next_microservice_package():
#     assert False
#
#
# def test_select_next_microservice_package_out_of_current_contracts():
#     assert False
#
#
# def test_is_package_corresponds_bundle_current_contracts():
#     assert False
#
#
# def test_remove_packages_with_higher_contracts_then():
#     assert False
#
#
# def test_update_bundle_contracts():
#     assert False
#
#
# def test_rest_packages_to_find():
#     assert False
#
#
# def test__package_add():
#     assert False
