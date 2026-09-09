from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from alpha_evidence.schema_validation import DocumentValidationError, validate_public_evidence


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas/public-evidence.schema.json"
MANIFEST_SCHEMA = ROOT / "schemas/release-manifest.schema.json"


def write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


@pytest.mark.parametrize("schema_path", [SCHEMA, MANIFEST_SCHEMA])
def test_schemas_are_valid_and_objects_are_closed(schema_path):
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    open_objects = []
    def visit(value, location="$"):
        if isinstance(value, dict):
            if value.get("type") == "object" and value.get("additionalProperties") is not False:
                open_objects.append(location)
            for key, child in value.items(): visit(child, f"{location}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value): visit(child, f"{location}[{index}]")
    visit(schema)
    assert open_objects == []


def test_valid_synthetic_evidence_passes(tmp_path, synthetic_evidence):
    assert validate_public_evidence(write(tmp_path, synthetic_evidence), SCHEMA) == synthetic_evidence


def test_unknown_fields_and_bad_dates_fail(tmp_path, synthetic_evidence):
    changed = dict(synthetic_evidence, unexpected=True)
    with pytest.raises(DocumentValidationError, match="Additional properties"):
        validate_public_evidence(write(tmp_path, changed), SCHEMA)
    changed = dict(synthetic_evidence, generated_at_utc="not-a-date")
    with pytest.raises(DocumentValidationError):
        validate_public_evidence(write(tmp_path, changed), SCHEMA)


def test_non_json_non_object_nonstandard_and_duplicate_documents_fail(tmp_path):
    path = tmp_path / "evidence.json"
    for payload, message in (("not json", "valid UTF-8 JSON"), ("[]", "JSON objects"), ('{"x":NaN}', "non-standard numeric"), ('{"x":1,"x":2}', "duplicate JSON")):
        path.write_text(payload, encoding="utf-8")
        with pytest.raises(DocumentValidationError, match=message):
            validate_public_evidence(path, SCHEMA)
