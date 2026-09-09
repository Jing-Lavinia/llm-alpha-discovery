from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

class DocumentValidationError(ValueError):
    """Raised when a JSON document does not satisfy its public contract."""


_FORMAT_CHECKER = FormatChecker()


@_FORMAT_CHECKER.checks("date", raises=(TypeError, ValueError))
def _is_iso_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    return date.fromisoformat(value).isoformat() == value


@_FORMAT_CHECKER.checks("date-time", raises=(TypeError, ValueError))
def _is_timezone_aware_iso_datetime(value: object) -> bool:
    if not isinstance(value, str) or "T" not in value:
        return False
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.tzinfo is not None


def load_json(path: Path) -> Any:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-standard numeric constant {value!r}")

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON object key {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=reject_constant,
            object_pairs_hook=unique_object,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise DocumentValidationError(f"cannot read valid UTF-8 JSON from {path}: {exc}") from exc


def _json_location(parts: list[object]) -> str:
    location = "$"
    for part in parts:
        location += f"[{part}]" if isinstance(part, int) else f".{part}"
    return location


def validate_json_document(document: Any, schema: dict[str, Any]) -> None:
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise DocumentValidationError(f"invalid JSON Schema: {exc.message}") from exc

    # Register the two formats used by this project explicitly. Some minimal
    # jsonschema installations omit their optional RFC-3339 dependency and
    # would otherwise accept malformed dates silently.
    validator = Draft202012Validator(schema, format_checker=_FORMAT_CHECKER)
    errors = sorted(validator.iter_errors(document), key=lambda error: list(error.path))
    if errors:
        detail = "; ".join(
            f"{_json_location(list(error.path))}: {error.message}" for error in errors
        )
        raise DocumentValidationError(detail)


def validate_public_evidence(
    evidence_path: Path,
    schema_path: Path,
) -> dict[str, Any]:
    document = load_json(evidence_path)
    schema = load_json(schema_path)
    if not isinstance(document, dict) or not isinstance(schema, dict):
        raise DocumentValidationError("evidence and schema must both be JSON objects")
    validate_json_document(document, schema)
    return document
