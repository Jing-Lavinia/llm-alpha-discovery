from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from alpha_evidence.manifest import (
    ManifestValidationError,
    read_allowlist,
    sha256_file,
    validate_release_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "release-manifest.schema.json"


def _manifest(root: Path, relative_paths: list[str]) -> dict:
    return {
        "manifest_version": "1.0",
        "release_id": "SYNTHETIC-RELEASE",
        "generated_at_utc": "2030-01-15T00:00:00Z",
        "files": [
            {
                "path": relative,
                "bytes": (root / relative).stat().st_size,
                "sha256": sha256_file(root / relative),
            }
            for relative in relative_paths
        ],
    }


def _write_manifest(root: Path, payload: dict) -> Path:
    path = root / "release-manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_manifest_verifies_exact_allowlist_size_and_hash(tmp_path) -> None:
    (tmp_path / "evidence").mkdir()
    (tmp_path / "figures").mkdir()
    (tmp_path / "evidence" / "aggregate.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "figures" / "summary.png").write_bytes(b"synthetic-image-bytes")
    expected = ["evidence/aggregate.json", "figures/summary.png"]
    path = _write_manifest(tmp_path, _manifest(tmp_path, expected))

    validated = validate_release_manifest(
        path, tmp_path, SCHEMA, expected_paths=expected
    )

    assert [entry["path"] for entry in validated["files"]] == expected


def test_manifest_detects_content_and_byte_size_tampering(tmp_path) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text("{}", encoding="utf-8")
    manifest = _write_manifest(tmp_path, _manifest(tmp_path, ["payload.json"]))

    payload.write_text('{"changed":true}', encoding="utf-8")
    with pytest.raises(ManifestValidationError, match="byte-size mismatch"):
        validate_release_manifest(manifest, tmp_path, SCHEMA)

    document = _manifest(tmp_path, ["payload.json"])
    document["files"][0]["sha256"] = "0" * 64
    manifest = _write_manifest(tmp_path, document)
    with pytest.raises(ManifestValidationError, match="SHA-256 mismatch"):
        validate_release_manifest(manifest, tmp_path, SCHEMA)


def test_manifest_schema_rejects_extra_properties(tmp_path) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text("{}", encoding="utf-8")
    document = _manifest(tmp_path, ["payload.json"])
    document["files"][0]["comment"] = "not allowlisted"

    with pytest.raises(ManifestValidationError, match="Additional properties"):
        validate_release_manifest(
            _write_manifest(tmp_path, document), tmp_path, SCHEMA
        )


def test_manifest_rejects_duplicates_unsorted_entries_and_allowlist_drift(tmp_path) -> None:
    for name in ("a.json", "b.json"):
        (tmp_path / name).write_text("{}", encoding="utf-8")

    duplicated = _manifest(tmp_path, ["a.json", "a.json"])
    with pytest.raises(ManifestValidationError, match="duplicate"):
        validate_release_manifest(
            _write_manifest(tmp_path, duplicated), tmp_path, SCHEMA
        )

    unsorted = _manifest(tmp_path, ["b.json", "a.json"])
    with pytest.raises(ManifestValidationError, match="sorted"):
        validate_release_manifest(
            _write_manifest(tmp_path, unsorted), tmp_path, SCHEMA
        )

    valid = _manifest(tmp_path, ["a.json"])
    with pytest.raises(ManifestValidationError, match="allowlist mismatch"):
        validate_release_manifest(
            _write_manifest(tmp_path, valid),
            tmp_path,
            SCHEMA,
            expected_paths=["a.json", "b.json"],
        )


@pytest.mark.parametrize(
    "unsafe",
    ["../escape.json", "/" + "tmp/escape.json", "a\\b.json", "./a.json"],
)
def test_manifest_rejects_unsafe_paths_before_reading_files(tmp_path, unsafe: str) -> None:
    document = {
        "manifest_version": "1.0",
        "release_id": "SYNTHETIC-RELEASE",
        "generated_at_utc": "2030-01-15T00:00:00Z",
        "files": [{"path": unsafe, "bytes": 0, "sha256": "0" * 64}],
    }

    with pytest.raises(ManifestValidationError):
        validate_release_manifest(
            _write_manifest(tmp_path, document), tmp_path, SCHEMA
        )


def test_manifest_rejects_symlinks_even_when_target_stays_inside_root(tmp_path) -> None:
    target = tmp_path / "target.json"
    target.write_text("{}", encoding="utf-8")
    link = tmp_path / "linked.json"
    try:
        os.symlink(target.name, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are unavailable on this platform")
    manifest = _write_manifest(tmp_path, _manifest(tmp_path, ["linked.json"]))

    with pytest.raises(ManifestValidationError, match="symlink"):
        validate_release_manifest(manifest, tmp_path, SCHEMA)


def test_manifest_cannot_list_itself(tmp_path) -> None:
    manifest_path = tmp_path / "release-manifest.json"
    # The self-entry cannot be made cryptographically self-consistent, but the
    # validator should reject the design before attempting a hash comparison.
    document = {
        "manifest_version": "1.0",
        "release_id": "SYNTHETIC-RELEASE",
        "generated_at_utc": "2030-01-15T00:00:00Z",
        "files": [
            {
                "path": "release-manifest.json",
                "bytes": 0,
                "sha256": "0" * 64,
            }
        ],
    }
    manifest_path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ManifestValidationError, match="must not list itself"):
        validate_release_manifest(manifest_path, tmp_path, SCHEMA)


def test_allowlist_parser_requires_canonical_sorted_unique_paths(tmp_path) -> None:
    allowlist = tmp_path / "allowlist.txt"
    allowlist.write_text("# comment\na.json\nb.json\n", encoding="utf-8")
    assert read_allowlist(allowlist) == ("a.json", "b.json")

    allowlist.write_text("b.json\na.json\n", encoding="utf-8")
    with pytest.raises(ManifestValidationError, match="sorted"):
        read_allowlist(allowlist)

    allowlist.write_text("a.json\na.json\n", encoding="utf-8")
    with pytest.raises(ManifestValidationError, match="duplicate"):
        read_allowlist(allowlist)


def test_checked_in_release_manifest_verifies_exact_allowlist() -> None:
    allowlist = read_allowlist(ROOT / "evidence" / "release-allowlist.txt")

    validated = validate_release_manifest(
        ROOT / "evidence" / "release-manifest.v1.json",
        ROOT,
        SCHEMA,
        expected_paths=allowlist,
    )

    assert validated["release_id"] == "LLM-ALPHA-DISCOVERY"
