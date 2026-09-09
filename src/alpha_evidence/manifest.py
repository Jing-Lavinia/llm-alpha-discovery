from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from .schema_validation import load_json, validate_json_document


class ManifestValidationError(ValueError):
    """Raised when an evidence release manifest is unsafe or inconsistent."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative_path(raw: str) -> PurePosixPath:
    if not raw or "\\" in raw:
        raise ManifestValidationError(f"unsafe manifest path: {raw!r}")
    path = PurePosixPath(raw)
    if path.is_absolute() or path.as_posix() != raw:
        raise ManifestValidationError(f"manifest path is not canonical and relative: {raw!r}")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ManifestValidationError(f"manifest path contains traversal: {raw!r}")
    return path


def read_allowlist(path: Path) -> tuple[str, ...]:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    for line in lines:
        _safe_relative_path(line)
    if len(lines) != len(set(lines)):
        raise ManifestValidationError("release allowlist contains duplicate paths")
    if lines != sorted(lines):
        raise ManifestValidationError("release allowlist must be sorted")
    return tuple(lines)


def _reject_symlink_components(root: Path, relative: PurePosixPath) -> Path:
    candidate = root
    for part in relative.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise ManifestValidationError(
                f"manifest path uses a symlink: {relative.as_posix()}"
            )
    return candidate


def validate_release_manifest(
    manifest_path: Path,
    repository_root: Path,
    schema_path: Path,
    *,
    expected_paths: Iterable[str] | None = None,
) -> dict[str, Any]:
    root = repository_root.resolve(strict=True)
    if not root.is_dir():
        raise ManifestValidationError("repository root must be a directory")
    manifest = load_json(manifest_path)
    schema = load_json(schema_path)
    if not isinstance(manifest, dict) or not isinstance(schema, dict):
        raise ManifestValidationError("manifest and schema must be JSON objects")
    try:
        validate_json_document(manifest, schema)
    except ValueError as exc:
        raise ManifestValidationError(str(exc)) from exc

    entries = manifest["files"]
    paths = [entry["path"] for entry in entries]
    if paths != sorted(paths):
        raise ManifestValidationError("manifest file records must be sorted by path")
    if len(paths) != len(set(paths)):
        raise ManifestValidationError("manifest contains duplicate paths")

    if expected_paths is not None:
        expected = tuple(expected_paths)
        if len(expected) != len(set(expected)):
            raise ManifestValidationError("expected path allowlist contains duplicates")
        if set(paths) != set(expected):
            missing = sorted(set(expected) - set(paths))
            unexpected = sorted(set(paths) - set(expected))
            raise ManifestValidationError(
                f"manifest/allowlist mismatch; missing={missing}, unexpected={unexpected}"
            )

    try:
        manifest_relative = manifest_path.resolve(strict=True).relative_to(root).as_posix()
    except ValueError:
        manifest_relative = None

    for entry in entries:
        relative = _safe_relative_path(entry["path"])
        if manifest_relative == relative.as_posix():
            raise ManifestValidationError("release manifest must not list itself")
        candidate = _reject_symlink_components(root, relative)
        if not candidate.is_file():
            raise ManifestValidationError(f"manifest file is missing: {relative.as_posix()}")
        try:
            candidate.resolve(strict=True).relative_to(root)
        except ValueError as exc:
            raise ManifestValidationError(
                f"manifest path escapes repository root: {relative.as_posix()}"
            ) from exc
        observed_bytes = candidate.stat().st_size
        if observed_bytes != entry["bytes"]:
            raise ManifestValidationError(
                f"byte-size mismatch for {relative.as_posix()}: "
                f"expected {entry['bytes']}, observed {observed_bytes}"
            )
        observed_hash = sha256_file(candidate)
        if observed_hash != entry["sha256"]:
            raise ManifestValidationError(
                f"SHA-256 mismatch for {relative.as_posix()}"
            )
    return manifest
