from addict import Dict

from contracts.contract import Contract
from contracts.package import Package
from crosspm.adapters.artifactoryaql2 import ArtifactoryAql2

def test_parse_contracts_from_items_find_results():
    assert ArtifactoryAql2.parse_contracts_from_items_find_results([Dict({'key': 'contracts.db', 'value': '12'})]) \
        == {'contracts.db': '12'}
    assert ArtifactoryAql2.parse_contracts_from_items_find_results([Dict({'key': 'contracts.db', 'value': '2.5.230'})]) \
        == {'contracts.db': '2.5.230'}


