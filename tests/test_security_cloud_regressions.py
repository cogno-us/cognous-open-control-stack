"""Independent admission mutations from the 2026-10-16 static review."""
import copy
import json
from pathlib import Path
import pytest
from tools import collateral_evidence_snapshot as collateral
from tools import verify_publication_inventory as inventory
from tools.bounded_input import loads, read_bytes

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('field', ['documents', 'historical_snapshots'])
def test_missing_collateral_inventory_fails(field):
    m=collateral.load_manifest(ROOT/'collateral/evidence-snapshot.json')
    m[field]=[]
    with pytest.raises(collateral.SnapshotError,match='exact document'):
        collateral.validate_data(m)


@pytest.mark.parametrize('path', ['/tmp/external.md', '../README.md'])
def test_collateral_canonical_inventory_refuses_substitution(path):
    m=collateral.load_manifest(ROOT/'collateral/evidence-snapshot.json')
    m['documents'][0]['path']=path
    with pytest.raises(collateral.SnapshotError):collateral.validate_data(m)


def test_excluded_digest_and_source_must_be_valid():
    m=inventory.load_manifest(ROOT/'docs/releases/distribution-closeout-2026-10-15/manifest.json')
    m['excluded_files'][0]['source_commit']='0'*40
    with pytest.raises(inventory.InventoryError,match='excluded provenance'):
        inventory.validate_manifest(m)


@pytest.mark.parametrize('value', [b'{"x":1,"x":2}', b'['*40+b'0'+b']'*40, b'{"x":NaN}'])
def test_json_admission_refuses_ambiguous_or_excessive_input(value):
    with pytest.raises(ValueError):loads(value)


def test_read_is_bounded_before_json_parse(tmp_path):
    p=tmp_path/'large';p.write_bytes(b'x'*65)
    with pytest.raises(ValueError,match='budget'):read_bytes(p,64)
