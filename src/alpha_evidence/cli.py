from __future__ import annotations

import argparse
from pathlib import Path

from .manifest import read_allowlist, validate_release_manifest
from .schema_validation import validate_public_evidence


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="alpha-evidence",
        description="Validate the published aggregate evidence and artifact manifest.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    evidence = subcommands.add_parser("evidence", help="validate aggregate evidence")
    evidence.add_argument("evidence", type=Path)
    evidence.add_argument(
        "--schema", type=Path, default=Path("schemas/public-evidence.schema.json")
    )
    manifest = subcommands.add_parser("manifest", help="verify released artifacts")
    manifest.add_argument("manifest", type=Path)
    manifest.add_argument("--root", type=Path, default=Path.cwd())
    manifest.add_argument(
        "--schema", type=Path, default=Path("schemas/release-manifest.schema.json")
    )
    manifest.add_argument("--allowlist", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "evidence":
        validate_public_evidence(args.evidence, args.schema)
        print("public evidence: valid")
        return 0
    if args.command == "manifest":
        validate_release_manifest(
            args.manifest,
            args.root,
            args.schema,
            expected_paths=read_allowlist(args.allowlist),
        )
        print("release manifest: valid")
        return 0
    raise AssertionError(f"unhandled command: {args.command}")
