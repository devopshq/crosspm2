import pytest

from crosspm.contracts.package import Package
from crosspm.adapters.artifactoryaql2 import remove_package_versions_with_missing_contracts

@pytest.mark.parametrize(
    "test_case",
    [
        {
            'package_versions': [('db', 4, [('c.db', 1)])],
            'package_contracts': 'c.db',
            'packages_with_all_contracts': [('db', 4, [('c.db', 1)])],
            'packages_with_missing_contracts': {}
        },
        {
            'package_versions': [('db', 4, [('c.db', 1)])],
            'package_contracts': 'c.db;c.rest',
            'packages_with_all_contracts': [],
            'packages_with_missing_contracts': {('db', 4): ['c.rest']}
        },
        {
            'package_versions': [('db', 4, [('c.db', 1), ('c.rest', 1)])],
            'package_contracts': 'c.db',
            'packages_with_all_contracts': [('db', 4, [('c.db', 1)])],
            'packages_with_missing_contracts': {}
        },
        {
            'package_versions': [
                 ('db', 4, [('c.db', 1), ('c.rest', 1)]),
                 ('db', 5, [('c.db', 1)]),
                 ('db', 6, []),
                 ('db', 7, [('c.rest', 1)])
            ],
            'package_contracts': 'c.db',
            'packages_with_all_contracts': [('db', 4, [('c.db', 1)]), ('db', 5, [('c.db', 1)])],
            'packages_with_missing_contracts': {('db', 6) : ['c.db'], ('db', 7) : ['c.db']}
        },
    ]
)
def test_remove_package_versions_with_missing_contracts(test_case):
    package_versions = [Package.create_package(x) for x in test_case['package_versions']]
    package_contracts = test_case['package_contracts']
    expected_packages_with_all_contracts = [Package.create_package(x) for x in test_case['packages_with_all_contracts']]
    expected_packages_with_missing_contracts = {Package.create_package(p): c for p, c in test_case['packages_with_missing_contracts'].items()}

    packages_with_all_contracts, packages_with_missing_contracts = \
        remove_package_versions_with_missing_contracts(package_versions, package_contracts)

    assert packages_with_all_contracts == expected_packages_with_all_contracts
    assert packages_with_missing_contracts == expected_packages_with_missing_contracts
