from crosspm.contracts.package_version import PackageVersion

def test_package_version():
    assert PackageVersion("1.2.3") < PackageVersion("10.2.3")
    assert PackageVersion("1.3") == PackageVersion("1.3.0")
    assert PackageVersion("1.3") < PackageVersion("1.3.1")
    assert PackageVersion("1.2.3") < PackageVersion("1.2.3-feature1-super-puper")

    assert PackageVersion("1.2.3") != PackageVersion("1.2.3-feature1-super-puper")
    assert PackageVersion("1.3-SS7AD") != PackageVersion("1.3")
    assert PackageVersion("1.3-SS7AD") != PackageVersion("1.3-TEST")
    assert PackageVersion("1.3-SS7AD") == PackageVersion("1.3-SS7AD")
    assert PackageVersion("1.3-123") < PackageVersion("1.3-124")
    assert PackageVersion("1.3-124") > PackageVersion("1.3-123")
    assert PackageVersion("1.3-ABC") == PackageVersion("1.3-abc")
    assert PackageVersion("1.3-a") < PackageVersion("1.3-aa")
    assert PackageVersion("1.3-a") < PackageVersion("1.3-ba")


def test_package_version_properties():
    package_version = PackageVersion("1.2.3-feature1-super-puper")

    assert 1 == package_version.major
    assert 2 == package_version.minor
    assert 3 == package_version.micro
    assert 'feature1.super.puper' == package_version.local

