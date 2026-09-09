#!/usr/bin/env python3
"""Create the public checksum manifest from the explicit release allowlist."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / "evidence/release-allowlist.txt"
EVIDENCE = ROOT / "evidence/aggregate-evidence.v3.json"
OUTPUT = ROOT / "evidence/release-manifest.v1.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _paths() -> list[str]:
    paths = [
        line.strip()
        for line in ALLOWLIST.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if paths != sorted(set(paths)):
        raise ValueError("release allowlist must be sorted and unique")
    for raw in paths:
        relative = PurePosixPath(raw)
        if relative.is_absolute() or ".." in relative.parts or relative.as_posix() != raw:
            raise ValueError(f"unsafe release path: {raw!r}")
        target = ROOT / relative
        if target.is_symlink() or not target.is_file():
            raise ValueError(f"missing or linked release file: {raw}")
    return paths


def main() -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    paths = _paths()
    manifest = {
        "manifest_version": "1.0",
        "release_id": evidence["study_id"],
        "generated_at_utc": evidence["generated_at_utc"],
        "files": [
            {
                "path": raw,
                "bytes": (ROOT / raw).stat().st_size,
                "sha256": _sha256(ROOT / raw),
            }
            for raw in paths
        ],
    }
    OUTPUT.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT.relative_to(ROOT)} with {len(paths)} files")


if __name__ == "__main__":
    main()
