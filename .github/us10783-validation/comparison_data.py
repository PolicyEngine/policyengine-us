"""Pure typed parameter records, complete grids, and union comparisons.

No country imports or process actions belong in this module.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

ORIGINAL_YEARS = (
    2013,
    2015,
    2018,
    2020,
    2024,
    2025,
    2026,
    2027,
    2028,
    2029,
    2030,
    2031,
    2032,
    2033,
    2034,
    2035,
    2036,
    2037,
    2040,
    2045,
    2050,
    2060,
    2075,
    2090,
    2100,
    2110,
)
TRUSTEES_VIEW_YEARS = (
    2027,
    2034,
    2035,
    2036,
    2037,
    2040,
    2045,
    2050,
    2060,
    2075,
    2090,
    2100,
)
HISTORY_PATH = "gov.irs.deductions.standard.dependent.additional_earned_income"
HISTORY_DATES = tuple(f"{year:04d}-01-01" for year in (1, 1997, *range(1998, 2013)))
ORIGINAL_DATES = tuple(f"{year}-01-01" for year in ORIGINAL_YEARS)
ABSENT_SIDE = {"kind": "ABSENT_SIDE"}


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def type_name(value) -> str:
    return f"{type(value).__module__}.{type(value).__qualname__}"


def encode_value(value) -> dict:
    """Preserve type and float identity; unsupported values remain explicit."""
    # NumPy float64/str_ inherit Python built-ins but still need item() to
    # become exact native scalars before type validation and repr capture.
    if (
        type(value).__module__.startswith("numpy")
        and getattr(value, "shape", None) == ()
    ):
        try:
            scalar = value.item()
            if type(scalar) is type(value):
                raise TypeError("Scalar item() did not produce a native scalar")
            return encode_value(scalar)
        except Exception as error:
            return {
                "kind": "UNSUPPORTED",
                "python_type": type_name(value),
                "repr": repr(value),
                "conversion_error": repr(error),
            }
    if value is None:
        return {"kind": "NULL", "value": None}
    if isinstance(value, bool):
        return {"kind": "BOOL", "value": value}
    if isinstance(value, int):
        return {"kind": "INT", "value": value}
    if isinstance(value, float):
        if not math.isfinite(value):
            name = "nan" if math.isnan(value) else ("+inf" if value > 0 else "-inf")
            return {"kind": "NONFINITE", "value": name, "float_hex": value.hex()}
        return {
            "kind": "FLOAT",
            "value": value,
            "decimal": repr(value),
            "float_hex": value.hex(),
        }
    if isinstance(value, str):
        return {"kind": "STRING", "value": value}
    result = {
        "kind": "UNSUPPORTED",
        "python_type": type_name(value),
        "repr": repr(value),
    }
    if hasattr(value, "shape"):
        result["shape"] = list(value.shape)
    if hasattr(value, "dtype"):
        result["dtype"] = str(value.dtype)
    if hasattr(value, "tolist"):
        try:
            result["data_repr"] = repr(value.tolist())
        except Exception as error:
            result["conversion_error"] = repr(error)
    return result


def lookup_value(parameter, date: str) -> dict:
    try:
        value = parameter(date)
    except Exception as error:
        return {
            "kind": "LOOKUP_ERROR",
            "exception_type": type_name(error),
            "message": str(error),
        }
    try:
        return encode_value(value)
    except Exception as error:
        return {
            "kind": "UNSUPPORTED",
            "python_type": type_name(value),
            "repr": "<representation failed>",
            "conversion_error": repr(error),
        }


def names_catalog(names) -> list[str]:
    names = list(names)
    if any(not isinstance(name, str) or not name for name in names):
        raise ValueError("Invalid Parameter catalog name")
    if len(names) != len(set(names)):
        raise ValueError("Duplicate Parameter catalog name")
    return sorted(names)


def dates_for(path: str, dates, history: dict) -> list[str]:
    return sorted(set(dates) | set(history.get(path, ())))


def expected_keys(catalog, dates, history, mode):
    for name in names_catalog(catalog):
        for date in dates_for(name, dates, history):
            yield name, date, mode


def row_key(row):
    return row["path"], row["date"], row["mode"]


def validate_typed(value):
    kind = value.get("kind")
    if kind == "FLOAT":
        number = value.get("value")
        if type(number) is not float or not math.isfinite(number):
            raise ValueError("Invalid finite float")
        if value.get("float_hex") != number.hex() or value.get("decimal") != repr(
            number
        ):
            raise ValueError("Float identity does not match")
    elif kind == "INT" and type(value.get("value")) is not int:
        raise ValueError("Invalid integer")
    elif kind == "BOOL" and type(value.get("value")) is not bool:
        raise ValueError("Invalid boolean")
    elif kind == "STRING" and type(value.get("value")) is not str:
        raise ValueError("Invalid string")
    elif kind == "NULL" and value.get("value") is not None:
        raise ValueError("Invalid null")
    elif kind == "NONFINITE" and value.get("value") not in {"nan", "+inf", "-inf"}:
        raise ValueError("Invalid nonfinite value")
    elif kind == "LOOKUP_ERROR" and not {"exception_type", "message"} <= value.keys():
        raise ValueError("Incomplete lookup error")
    elif kind == "UNSUPPORTED" and not {"python_type", "repr"} <= value.keys():
        raise ValueError("Incomplete unsupported value")
    elif kind not in {
        "FLOAT",
        "INT",
        "BOOL",
        "STRING",
        "NULL",
        "NONFINITE",
        "LOOKUP_ERROR",
        "UNSUPPORTED",
    }:
        raise ValueError(f"Unknown export value kind: {kind}")


def validated_rows(catalog, dates, history, mode, rows):
    """Ordered full-grid validation without allocating millions of key tuples."""
    if not dates or len(dates) != len(set(dates)):
        raise ValueError("Invalid date profile")
    sentinel = object()
    for expected, row in itertools.zip_longest(
        expected_keys(catalog, dates, history, mode), rows, fillvalue=sentinel
    ):
        if row is sentinel:
            raise ValueError(f"MISSING_EXPORT_ROW: {expected}")
        if expected is sentinel:
            raise ValueError(f"EXTRA_EXPORT_ROW: {row_key(row)}")
        actual = row_key(row)
        if actual != expected:
            reason = (
                "MISSING_EXPORT_ROW" if actual > expected else "EXTRA_OR_DUPLICATE_ROW"
            )
            raise ValueError(f"{reason}: expected {expected}, observed {actual}")
        validate_typed(row["value"])
        yield row


def exact_equal(left, right):
    return left == right


def tolerance_equal(left, right):
    if left["kind"] in {"INT", "FLOAT"} and right["kind"] in {"INT", "FLOAT"}:
        return math.isclose(left["value"], right["value"], rel_tol=1e-12, abs_tol=1e-9)
    return exact_equal(left, right)


def compare_streams(sides: dict, *, allow_cross_mode=False):
    """Validate each independent grid, then join their catalog union as typed data.

    A side supplies catalog/dates/history/mode/rows. Row generators are consumed
    completely; a matching dropped path cannot certify itself via emitted counts.
    """
    if len(sides) < 2:
        raise ValueError("At least two sides required")
    profiles = {
        (tuple(s["dates"]), json.dumps(s["history"], sort_keys=True))
        for s in sides.values()
    }
    if len(profiles) != 1:
        raise ValueError("Incompatible date/history profiles")
    modes = {name: side["mode"] for name, side in sides.items()}
    if len(set(modes.values())) != 1 and not allow_cross_mode:
        raise ValueError("Cross-mode comparison requires explicit opt-in")
    cursors, present = {}, {}
    for name, side in sides.items():
        side["catalog"] = names_catalog(side["catalog"])
        present[name] = set(side["catalog"])
        cursors[name] = iter(
            validated_rows(
                side["catalog"],
                side["dates"],
                side["history"],
                side["mode"],
                side["rows"],
            )
        )
    first = next(iter(sides.values()))
    union = sorted(set().union(*present.values()))
    for path in union:
        for date in dates_for(path, first["dates"], first["history"]):
            values = {}
            for name in sides:
                if path not in present[name]:
                    values[name] = dict(ABSENT_SIDE)
                else:
                    row = next(cursors[name])
                    if row_key(row) != (path, date, sides[name]["mode"]):
                        raise ValueError("Grid cursor mismatch")
                    values[name] = row["value"]
            baseline = next(iter(values.values()))
            exact = all(exact_equal(baseline, value) for value in values.values())
            tolerated = all(
                tolerance_equal(baseline, value) for value in values.values()
            )
            if not exact:
                yield {
                    "path": path,
                    "date": date,
                    "mode": first["mode"]
                    if len(set(modes.values())) == 1
                    else "cross_mode",
                    "side_modes": modes,
                    "sides": values,
                    "legacy_tolerance_equal": tolerated,
                }
    for cursor in cursors.values():
        if next(cursor, None) is not None:
            raise ValueError("EXTRA_EXPORT_ROW after union")


def read_export(manifest_path):
    path = Path(manifest_path).resolve()
    manifest = json.loads(path.read_text())
    if (
        manifest.get("complete") is not True
        or manifest.get("grid_validated") is not True
    ):
        raise ValueError("Incomplete export")
    records = manifest["outputs"]
    for record in records.values():
        if digest(Path(record["path"])) != record["sha256"]:
            raise ValueError("Output checksum mismatch")
    catalog_record = json.loads(Path(records["catalog"]["path"]).read_text())
    if (
        catalog_record["source_commit"] != manifest["source"]["commit"]
        or catalog_record["mode"] != manifest["mode"]
    ):
        raise ValueError("Catalog source/mode identity mismatch")
    catalog = catalog_record["names"]

    def rows():
        with Path(records["values"]["path"]).open() as stream:
            for line in stream:
                yield json.loads(line)

    return manifest, {
        "catalog": catalog,
        "dates": manifest["dates"],
        "history": manifest["history"],
        "mode": manifest["mode"],
        "rows": rows(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--side", action="append", required=True, help="NAME=completed-manifest.json"
    )
    parser.add_argument("--out", required=True)
    parser.add_argument("--legacy-out", required=True)
    parser.add_argument("--cross-mode", action="store_true")
    args = parser.parse_args()
    sides, manifests = {}, {}
    for spec in args.side:
        name, path = spec.split("=", 1)
        if name in sides:
            raise ValueError("Duplicate side name")
        manifests[name], sides[name] = read_export(path)
    runtime_ids = {m["runtime_binding_sha256"] for m in manifests.values()}
    if len(runtime_ids) != 1:
        raise ValueError("Different runtime bindings")
    if (
        args.cross_mode
        and len({m["source"]["commit"] for m in manifests.values()}) != 1
    ):
        raise ValueError("Cross-mode changed-set comparison requires one source commit")
    out = Path(args.out)
    legacy_out = Path(args.legacy_out)
    if out.resolve() == legacy_out.resolve():
        raise ValueError("Raw and tolerance outputs must remain separate")
    partial = out.with_name(out.name + ".partial")
    legacy_partial = legacy_out.with_name(legacy_out.name + ".partial")
    count = legacy_count = 0
    with partial.open("x") as stream, legacy_partial.open("x") as legacy:
        for row in compare_streams(sides, allow_cross_mode=args.cross_mode):
            text = json.dumps(row, sort_keys=True, allow_nan=False) + "\n"
            stream.write(text)
            if not row["legacy_tolerance_equal"]:
                legacy.write(text)
                legacy_count += 1
            count += 1
    from atomic import write_new_json
    import os

    for temporary, final in ((partial, out), (legacy_partial, legacy_out)):
        os.link(temporary, final)
        temporary.unlink()
    summary = {
        "complete": True,
        "exact_difference_rows": count,
        "legacy_difference_rows": legacy_count,
        "raw": {"path": str(out), "sha256": digest(out)},
        "legacy": {"path": str(legacy_out), "sha256": digest(legacy_out)},
        "inputs": {
            name: {
                "source": m["source"],
                "mode": m["mode"],
                "bindings_sha256": m["bindings_sha256"],
            }
            for name, m in manifests.items()
        },
        "parity_approved": False,
    }
    write_new_json(out.with_name(out.name + ".manifest.json"), summary)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
