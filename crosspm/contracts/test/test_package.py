from crosspm.contracts.package import Package

def test_debain_package():
    assert Package.create_package_debian("tad-db_1.2.3-123_all.deb") > Package.create_package_debian("tad-db_1.2.3_all.deb")

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
