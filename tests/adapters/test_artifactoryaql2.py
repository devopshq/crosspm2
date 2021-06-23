import pytest

from crosspm.contracts.package import Package
from crosspm.adapters.artifactoryaql2 import remove_package_versions_with_missing_contracts

@pytest.mark.parametrize(
    "test_case",
    [
        {
            'package_versions': [('db', 4, 'contracts.db=1')],
            'package_contracts': ['contracts.db'],
            'packages_with_all_contracts': [('db', 4, 'contracts.db=1')],
            'packages_with_missing_contracts': {}
        },
        {
            'package_versions': [('db', 4, 'contracts.db=1')],
            'package_contracts': ['contracts.db', 'contracts.rest'],
            'packages_with_all_contracts': [],
            'packages_with_missing_contracts': {('db', 4): ['contracts.rest']}
        },
        {
            'package_versions': [('db', 4, 'contracts.db=1;contracts.rest=1')],
            'package_contracts': ['contracts.db'],
            'packages_with_all_contracts': [('db', 4, 'contracts.db=1')],
            'packages_with_missing_contracts': {}
        },
        {
            'package_versions': [
                 ('db', 4, 'contracts.db=1;contracts.rest=1'),
                 ('db', 5, 'contracts.db=1'),
                 ('db', 6, ''),
                 ('db', 7, 'contracts.rest=1')
            ],
            'package_contracts': ['contracts.db'],
            'packages_with_all_contracts': [('db', 4, 'contracts.db=1'), ('db', 5, 'contracts.db=1')],
            'packages_with_missing_contracts': {('db', 6) : ['contracts.db'], ('db', 7) : ['contracts.db']}
        },
    ]
)
def test_remove_package_versions_with_missing_contracts(test_case):
    package_versions = [Package.create_package_from_tuple(x) for x in test_case['package_versions']]
    package_contracts = test_case['package_contracts']
    expected_packages_with_all_contracts = [Package.create_package_from_tuple(x) for x in test_case['packages_with_all_contracts']]
    expected_packages_with_missing_contracts = {Package.create_package_from_tuple(p): c for p, c in test_case['packages_with_missing_contracts'].items()}

    packages_with_all_contracts, packages_with_missing_contracts = \
        remove_package_versions_with_missing_contracts(package_versions, package_contracts)

    assert packages_with_all_contracts == expected_packages_with_all_contracts
    assert packages_with_missing_contracts == expected_packages_with_missing_contracts
