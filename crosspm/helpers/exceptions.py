# -*- coding: utf-8 -*-

CROSSPM_ERRORCODES = (
    CROSSPM_ERRORCODE_SUCCESS,
    CROSSPM_ERRORCODE_UNKNOWN_ERROR,
    CROSSPM_ERRORCODE_WRONG_ARGS,
    CROSSPM_ERRORCODE_FILE_DEPS_NOT_FOUND,
    CROSSPM_ERRORCODE_WRONG_SYNTAX,
    CROSSPM_ERRORCODE_MULTIPLE_DEPS,
    CROSSPM_ERRORCODE_NO_FILES_TO_PACK,
    CROSSPM_ERRORCODE_SERVER_CONNECT_ERROR,
    CROSSPM_ERRORCODE_PACKAGE_NOT_FOUND,
    CROSSPM_ERRORCODE_PACKAGE_BRANCH_NOT_FOUND,
    CROSSPM_ERRORCODE_VERSION_PATTERN_NOT_MATCH,
    CROSSPM_ERRORCODE_UNKNOWN_OUT_TYPE,
    CROSSPM_ERRORCODE_FILE_IO,
    CROSSPM_ERRORCODE_CONFIG_NOT_FOUND,
    CROSSPM_ERRORCODE_CONFIG_IO_ERROR,
    CROSSPM_ERRORCODE_CONFIG_FORMAT_ERROR,
    CROSSPM_ERRORCODE_ADAPTER_ERROR,
    CROSSPM_ERRORCODE_UNKNOWN_ARCHIVE,
    CROSSPM_ERRORCODE_BUNDLE_NO_VALID_CONTRACTS_GRAPH,
    CROSSPM_ERRORCODE_BUNDLE_TRIGGER_PACKAGES_HAS_NO_VALID_CONTRACTS_GRAPH,
    CROSSPM_ERRORCODE_BUNDLE_TRIGGER_PACKAGE_HIDES_HIGHER_VERSION,
) = range(21)


class CrosspmException(Exception):
    def __init__(self, error_code, msg=''):
        super().__init__(msg)
        self.error_code = error_code
        self.msg = msg


class CrosspmBundleNoValidContractsGraph(CrosspmException):
    def __init__(self, msg=''):
        super().__init__(CROSSPM_ERRORCODE_BUNDLE_NO_VALID_CONTRACTS_GRAPH, msg)


class CrosspmBundleTriggerPackagesHasNoValidContractsGraph(CrosspmException):
    def __init__(self, trigger_packages):
        super().__init__(CROSSPM_ERRORCODE_BUNDLE_TRIGGER_PACKAGES_HAS_NO_VALID_CONTRACTS_GRAPH,
                         f"trigger_packages has no valid contracts graph : {trigger_packages}")


class CrosspmExceptionWrongArgs(CrosspmException):
    def __init__(self, msg=''):
        super().__init__(CROSSPM_ERRORCODE_WRONG_ARGS, msg)


class CrosspmBundleTriggerPackageHidesHigherVersion(CrosspmException):
    def __init__(self, trigger_package, package_with_higher_version):
        super().__init__(CROSSPM_ERRORCODE_BUNDLE_TRIGGER_PACKAGE_HIDES_HIGHER_VERSION,
                         f"trigger_package : {trigger_package} hides package {package_with_higher_version}")
