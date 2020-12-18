import io

from addict import Dict

from crosspm.output_formatters.deps_txt_lock_list_formatter import DepsTxtLockListFormatter

def get_packages():

    base = [
        ["db", "2.5.2", "/db_2.5.2_all.deb"],
        ["be",  "2.5.4",  "/project2.5/backend/be_2.5.4_all.deb"],
        ["ui", "2.5.3", "/ui_2.5.3_all.deb"],
    ]

    packages = Dict()
    for b in base:
        p = Dict()

        p.art_package.name = b[0]
        p.art_package.version = b[1]
        p.art_package.art_path.path_in_repo = b[2]

        packages[b[0]] = p

    return packages

etalon_deps_lock_file = """db  2.5.2  /db_2.5.2_all.deb
be  2.5.4  /project2.5/backend/be_2.5.4_all.deb
ui  2.5.3  /ui_2.5.3_all.deb"""


def test_write_packages_to_lock_file():
    deps_lock_stream = io.StringIO()
    DepsTxtLockListFormatter.write_packages_to_lock_file(deps_lock_stream, get_packages())
    deps_lock = deps_lock_stream.getvalue()
    assert etalon_deps_lock_file == deps_lock

def test_read_packages_from_lock_file():
    deps_lock_stream = io.StringIO(etalon_deps_lock_file)
    paths = DepsTxtLockListFormatter.read_packages_from_lock_file(deps_lock_stream)

    assert ["/db_2.5.2_all.deb", "/project2.5/backend/be_2.5.4_all.deb", "/ui_2.5.3_all.deb"] == paths
