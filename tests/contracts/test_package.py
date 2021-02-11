from addict import Dict
from crosspm.contracts.package import *

def test_debain_package():
    assert Package.create_package_debian("tad-db_1.2.3-123_all.deb") > Package.create_package_debian("tad-db_1.2.3_all.deb")

def test_parse_contracts_from_package_properties():
    assert parse_contracts_from_package_properties(Dict({'contracts.db': ['12']})) \
        == {'contracts.db': ['12']}
    assert parse_contracts_from_package_properties(Dict({'contracts.db': ['2.5.230']})) \
        == {'contracts.db': ['2.5.230']}
    assert parse_contracts_from_package_properties(Dict({'contracts.db': ['2.5.230'], 'contracts.rest': ['123']})) \
        == {'contracts.db': ['2.5.230'], 'contracts.rest': ['123']}
    assert parse_contracts_from_package_properties(Dict({'contracts.db': ['2.5.230'], 'contracts.rest': ['123']})) \
        != {'contracts.db': ['2.5.230'], 'contracts.rest': ['121']}

def test_parse_contracts_multiple_values_from_package_properties():
    assert parse_contracts_from_package_properties(Dict({'contracts.db': ['2.5.230', '3.4', '6.123'], 'contracts.rest': ['123', '456', '7890abcdef']})) \
        == {'contracts.db': ['2.5.230', '3.4', '6.123'], 'contracts.rest': ['123', '456', '7890abcdef']}

def test_parse_contracts_multiple_values_from_string():
    assert parse_contracts_from_string('contracts.db=2.5.230,3.4,6.123;contracts.rest=123,456,7890abcdef') \
        == {'contracts.db': ['2.5.230', '3.4', '6.123'], 'contracts.rest': ['123', '456', '7890abcdef']}

def test_create_package_from_tuple():
    p = Package.create_package_from_tuple(('db', '1', 'contracts.db=1'))

    assert p == Package('db', '1', {'contracts.db' : ['1']})

def test_package_to_str():
    p = Package('db', '1',
                {
                    'contracts.db': Contract('contracts.db', ['123', 'abcdef']),
                    'contracts.rest': Contract('contracts.rest', ['098', 'xyz']),
                })

    assert str(p) == "db.1(contracts.db['123', 'abcdef'];contracts.rest['098', 'xyz'])"

# def test_is_microservice(self):
#     assert False
#
# def test_is_contract_lower_then(self):
#     assert False
#
# def test_is_contract_higher_then(self):
#     assert False
#
# def test_is_any_contract_higher(self):
#     assert False
#
# def test_calc_contracts_intersection(self):
#     assert False
#
# def test_create_contracts(self):
#     assert False
#
# def test_create_contracts_from_dict(self):
#     assert False
#
# def test_create_package(self):
#     assert False
#
# def test_create_packages(self):
#     assert False
