import pytest

from crosspm.deps_txt_parsers.deps_simple import DepsTxtSimpleParser
from crosspm.package_parsers.debian_package_name_parser import DebianPackageNameParser

deps_txt = """be 2.6.*- contracts.db
ui 3.* contracts.rest;contracts.ui"""


@pytest.mark.parametrize(
    "test_package",
    [
        "be_2.6.123_amd64.deb",
        "ui_3.1.123_all.deb",
        "ui_3.1.123-feature890_all.deb",
        "ui_3.1.123-feature-super-long-name-890_all.deb",
        "ui_3.45.123_all.deb",
        "ui_3.45.123-feature890_all.deb",
        "ui_3.45.123-feature-super-long-name-890_all.deb",
    ]
)
def test_success_is_package_fullname_match_version_pattern(test_package):
    deps = DepsTxtSimpleParser(deps_txt.splitlines())
    assert deps.is_package_fullname_match_version_pattern(DebianPackageNameParser.parse_from_package_name(test_package))

@pytest.mark.parametrize(
    "test_package",
    [
        "be_2.5.123_amd64.deb",
        "be_3.6.123_amd64.deb",
        "be_2.6.123-feature1_amd64.deb",
        "ui_4.1.123_all.deb",
        "ui_4.1.123-feature-super-long-name-890_all.deb",
    ]
)
def test_failure_is_package_fullname_match_version_pattern(test_package):
    deps = DepsTxtSimpleParser(deps_txt.splitlines())
    assert not deps.is_package_fullname_match_version_pattern(DebianPackageNameParser.parse_from_package_name(test_package))
