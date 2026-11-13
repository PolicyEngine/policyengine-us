"""Export actual parameter trees after Linux source and resource checks."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import time

from atomic import sha256_file, write_new_json
from remote import (
    capture_resources,
    publish_provenance,
    resource_record,
    resource_snapshot,
    validate_source_record,
)
from comparison_data import (
    HISTORY_DATES,
    HISTORY_PATH,
    ORIGINAL_DATES,
    TRUSTEES_VIEW_YEARS,
    encode_value,
    lookup_value,
    names_catalog,
    validated_rows,
)


def frozen_json(record):
    path = Path(record["path"]).resolve()
    if sha256_file(path) != record["sha256"]:
        raise ValueError(f"Frozen input checksum mismatch: {path}")
    return json.loads(path.read_text())


def verify_source(source):
    """Verify a complete frozen manifest; this never creates a source archive."""
    root = Path(source["root"]).resolve()
    manifest = frozen_json(source["manifest"])
    if (manifest["commit"], manifest["tree"]) != (source["commit"], source["tree"]):
        raise ValueError("Source manifest identity mismatch")
    files = manifest["files"]
    expected_package = set()
    for relative, expected in files.items():
        path = (root / relative).resolve()
        if Path(relative).is_absolute() or not path.is_relative_to(root):
            raise ValueError("Unsafe source-manifest path")
        if sha256_file(path) != expected:
            raise ValueError(f"Source bytes changed: {relative}")
        if relative.startswith("policyengine_us/"):
            expected_package.add(relative)
    actual_package = {
        path.relative_to(root).as_posix()
        for path in (root / "policyengine_us").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    if not expected_package or actual_package != expected_package:
        raise ValueError("Frozen country package catalog differs")
    return root


def verify_runtime(binding):
    """Recheck Root's qualification evidence; no environment repair or resolver."""
    qualification = frozen_json(binding["qualification"])
    if qualification.get("core_version") != "3.36.0" or not qualification[
        "status"
    ].startswith("PASS"):
        raise ValueError("Released-Core qualification missing")
    if Path(sys.executable).resolve() != Path(binding["python_realpath"]).resolve():
        raise ValueError("Wrong interpreter")
    if str(Path(sys.prefix).resolve()) != str(Path(binding["prefix"]).resolve()):
        raise ValueError("Wrong private prefix")
    if (
        platform.machine() != binding["machine"]
        or platform.python_version() != binding["python_version"]
    ):
        raise ValueError("Wrong native Python/platform")
    core_root = Path(binding["core_root"]).resolve()
    import importlib.metadata

    if (
        importlib.metadata.version("policyengine-core") != qualification["core_version"]
        or importlib.metadata.version("policyengine-us")
        != qualification["country_distribution_version"]
    ):
        raise ValueError("Installed project/Core metadata changed after qualification")
    files = qualification["core_files_matched"]
    if len(files) != 195 or len({record["path"] for record in files}) != 195:
        raise ValueError("Incomplete Core wheel-file qualification")
    for record in files:
        path = (core_root.parent / record["path"]).resolve()
        if not path.is_relative_to(core_root) or sha256_file(path) != record["sha256"]:
            raise ValueError("Installed Core bytes changed")
    dependency = frozen_json(binding["dependency_evidence"])
    check = dependency.get("locked_environment_check", dependency)
    if check.get("exit") != 0:
        raise ValueError("Dependency evidence did not pass")
    argv = check["argv"]
    if not {"--check", "--dry-run", "--locked", "--offline", "dev"} <= set(argv):
        raise ValueError("Dependency evidence lacks the reviewed strict check flags")
    if "--inexact" in argv or "--no-install-project" in argv:
        raise ValueError("Final qualification requires the actual strict full check")
    return qualification


def verify_tables(tables):
    if tables["dates"] != list(ORIGINAL_DATES):
        raise ValueError("Original26 date profile changed")
    if tables["history"] != {HISTORY_PATH: list(HISTORY_DATES)}:
        raise ValueError("Known pre2013 history profile changed")
    if tables["trustees_view_dates"] != [
        f"{year}-01-01" for year in TRUSTEES_VIEW_YEARS
    ]:
        raise ValueError("Original Trustees view changed")
    if tables["trustees_defaults"] != {
        "start_year": 2035,
        "end_year": 2100,
        "projection_base_year": 2026,
    }:
        raise ValueError("Genuine Trustees defaults changed")


def assert_imports(root, core_root):
    for name, module in tuple(sys.modules.items()):
        if name == "policyengine_us" or name.startswith("policyengine_us."):
            base = root / "policyengine_us"
        elif name == "policyengine_core" or name.startswith("policyengine_core."):
            base = core_root
        else:
            continue
        location = getattr(module, "__file__", None)
        if location and not Path(location).resolve().is_relative_to(base):
            raise ValueError(f"Unexpected imported module origin: {name}")


def selector_metadata(module, baseline_parameters):
    assumption = module.TRUSTEES_CORE_THRESHOLD_ASSUMPTION
    key = (
        "uprating_parameters"
        if "uprating_parameters" in assumption
        else "uprating_parameter"
    )
    initial = module._iter_updatable_parameters(
        baseline_parameters.gov.irs, uprating_parameter=assumption[key]
    )
    public = getattr(module, "trustees_core_threshold_parameters", None)
    effective = public(baseline_parameters) if public else None
    return {
        "assumption": encode_value(assumption),
        "uprating_key": key,
        "uprating_indices": encode_value(assumption[key]),
        "initial": names_catalog(p.name for p in initial),
        "effective_available": effective is not None,
        "effective": names_catalog(p.name for p in effective)
        if effective is not None
        else None,
        "followers": [
            {"path": p.name, "uprating": encode_value(p.metadata.get("uprating"))}
            for p in (effective or initial)
        ],
    }


def export_entry(args):
    """Check the frozen runtime and construct one source/mode in a cold process."""
    bindings_path = Path(args.bindings).resolve()
    binding_sha = sha256_file(bindings_path)
    resources = resource_snapshot()
    resource_start_path = (
        Path(args.manifest_out)
        .resolve()
        .with_name(Path(args.manifest_out).name + ".resources-start.json")
    )
    start_record = resource_record("start", resources)
    start_record.update(
        bindings_sha256=binding_sha,
        source_sha_command=args.source_sha,
        tree_sha_command=args.tree_sha,
        mode_command=args.mode,
        at=datetime.now(timezone.utc).isoformat(),
    )
    write_new_json(resource_start_path, start_record)
    publish_provenance()
    image_id = os.environ.get("US10783_IMAGE_ID", "")
    if not image_id.startswith("sha256:") or len(image_id) != 71:
        raise ValueError("Missing frozen remote image identity")
    bindings = json.loads(bindings_path.read_text())
    if bindings.get("schema_version") != 1:
        raise ValueError("Unknown frozen binding schema")
    source = bindings["source"]
    validate_source_record(source)
    if (args.source_sha, args.tree_sha) != (source["commit"], source["tree"]):
        raise ValueError("Command/source identity mismatch")
    if os.environ.get("PYTHONDONTWRITEBYTECODE") != "1":
        raise ValueError("Bytecode writes must remain disabled")
    if any(
        name == "policyengine_us"
        or name.startswith("policyengine_us.")
        or name == "policyengine_core"
        or name.startswith("policyengine_core.")
        for name in sys.modules
    ):
        raise RuntimeError("Refuse a preloaded/warm country or Core")
    tables = bindings["tables"]
    verify_tables(tables)
    root = verify_source(source)
    qualification = verify_runtime(bindings["runtime"])
    core_root = Path(bindings["runtime"]["core_root"]).resolve()
    started = datetime.now(timezone.utc).isoformat()
    clock = time.monotonic()
    sys.path.insert(0, str(root))
    for package, expected in (
        ("policyengine_us", root / "policyengine_us/__init__.py"),
        ("policyengine_core", core_root / "__init__.py"),
    ):
        spec = importlib.util.find_spec(package)
        if spec is None or Path(spec.origin).resolve() != expected.resolve():
            raise ValueError(f"Wrong cold import origin: {package}")
    # Actual original dump API; no simulation, dataset or household is constructed.
    country = importlib.import_module("policyengine_us")
    core = importlib.import_module("policyengine_core")
    system_module = importlib.import_module("policyengine_us.system")
    parameter_module = importlib.import_module("policyengine_core.parameters")
    Parameter = parameter_module.Parameter
    assert_imports(root, core_root)
    baseline_parameters = system_module.system.parameters
    parameters = baseline_parameters
    selectors = None
    if args.mode == "trustees":
        trustees = importlib.import_module(
            "policyengine_us.reforms.ssa.trustees_core_thresholds"
        )
        selectors = selector_metadata(trustees, baseline_parameters)
        # Preserve the genuine original constructor and explicit unchanged defaults.
        reformed_system = country.CountryTaxBenefitSystem(
            reform=(
                trustees.create_trustees_core_thresholds_reform(
                    **tables["trustees_defaults"]
                ),
            )
        )
        parameters = reformed_system.parameters
    catalog = names_catalog(
        p.name for p in parameters.get_descendants() if isinstance(p, Parameter)
    )
    runtime_sha = hashlib.sha256(
        json.dumps(bindings["runtime"], sort_keys=True).encode()
    ).hexdigest()
    common = {
        "schema_version": 1,
        "source": source,
        "bindings_sha256": binding_sha,
        "runtime_binding_sha256": runtime_sha,
        "mode": args.mode,
        "dates": tables["dates"],
        "history": tables["history"],
        "trustees_view_dates": tables["trustees_view_dates"],
        "reform_arguments": tables["trustees_defaults"]
        if args.mode == "trustees"
        else None,
        "country_origin": country.__file__,
        "core_origin": core.__file__,
        "qualification": bindings["runtime"]["qualification"],
        "qualified_core_version": qualification["core_version"],
        "python": sys.executable,
        "python_realpath": str(Path(sys.executable).resolve()),
        "python_version": platform.python_version(),
        "machine": platform.machine(),
        "prefix": sys.prefix,
        "argv": sys.argv,
        "thread_environment": {
            name: os.environ.get(name)
            for name in (
                "OMP_NUM_THREADS",
                "OPENBLAS_NUM_THREADS",
                "MKL_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS",
                "NUMEXPR_NUM_THREADS",
            )
        },
        "started_utc": started,
        "parameter_count_observed": len(catalog),
        "helper_sha256": sha256_file(__file__),
        "selectors": selectors,
        "remote_resources": resources,
        "resource_start_sidecar": {
            "path": str(resource_start_path),
            "sha256": sha256_file(resource_start_path),
        },
        "image_id": image_id,
    }
    out = Path(args.out).resolve()
    manifest_out = Path(args.manifest_out).resolve()
    if args.probe_only:
        common["remote_resources_final"] = resource_snapshot()
        common.update(
            probe_only=True,
            complete=False,
            probe=lookup_value(
                parameters.gov.irs.deductions.standard.amount.SINGLE, "2027-01-01"
            ),
        )
        assert_imports(root, core_root)
        verify_source(source)
        common["elapsed_seconds"] = time.monotonic() - clock
        write_new_json(manifest_out, common)
        return common
    # Independent second traversal. Grid completeness derives from the earlier catalog.
    by_name = {}
    for parameter in parameters.get_descendants():
        if isinstance(parameter, Parameter):
            if parameter.name in by_name:
                raise ValueError("Duplicate parameter on emission traversal")
            by_name[parameter.name] = parameter
    if set(by_name) != set(catalog):
        raise ValueError("Parameter catalog changed between traversals")

    def rows():
        for name in sorted(by_name):
            dates = sorted(set(tables["dates"]) | set(tables["history"].get(name, ())))
            for date in dates:
                yield {
                    "path": name,
                    "date": date,
                    "mode": args.mode,
                    "value": lookup_value(by_name[name], date),
                }

    partial = out.with_name(out.name + ".partial")
    counts = {}
    row_count = 0
    with partial.open("x") as stream:
        for row in validated_rows(
            catalog, tables["dates"], tables["history"], args.mode, rows()
        ):
            stream.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
            kind = row["value"]["kind"]
            counts[kind] = counts.get(kind, 0) + 1
            row_count += 1
        stream.flush()
        os.fsync(stream.fileno())
    assert_imports(root, core_root)
    verify_source(source)
    verify_runtime(bindings["runtime"])
    common["remote_resources_final"] = resource_snapshot()
    if out.exists():
        raise FileExistsError(out)
    os.link(partial, out)
    partial.unlink()  # Only this export's newly created temporary output.
    catalog_out = out.with_name(out.name + ".catalog.json")
    write_new_json(
        catalog_out,
        {"names": catalog, "source_commit": source["commit"], "mode": args.mode},
    )
    history = {}
    for name in tables["history"]:
        if name in by_name:
            parameter = by_name[name]
            history[name] = {
                "metadata": encode_value(parameter.metadata),
                "stated": [
                    {
                        "instant": value.instant_str,
                        "value": encode_value(value.value),
                        "file_path": str(value.file_path)
                        if getattr(value, "file_path", None)
                        else None,
                        "is_stated": getattr(value, "file_path", None) is not None,
                    }
                    for value in parameter.values_list
                ],
            }
    common.update(
        complete=True,
        probe_only=False,
        grid_validated=True,
        rows_observed=row_count,
        value_kinds=counts,
        review_required=bool(counts.get("LOOKUP_ERROR") or counts.get("UNSUPPORTED")),
        history_details=history,
        elapsed_seconds=time.monotonic() - clock,
        ended_utc=datetime.now(timezone.utc).isoformat(),
        outputs={
            "values": {"path": str(out), "sha256": sha256_file(out)},
            "catalog": {"path": str(catalog_out), "sha256": sha256_file(catalog_out)},
        },
    )
    write_new_json(manifest_out, common)  # Completion manifest publishes last.
    return common


def run_export(args):
    failure = None
    try:
        return export_entry(args)
    except BaseException as error:
        failure = repr(error)[:1024]
        raise
    finally:
        record = capture_resources("final", failure)
        record.update(
            source_sha_command=args.source_sha,
            tree_sha_command=args.tree_sha,
            mode_command=args.mode,
            at=datetime.now(timezone.utc).isoformat(),
        )
        path = (
            Path(args.manifest_out)
            .resolve()
            .with_name(Path(args.manifest_out).name + ".resources-final.json")
        )
        try:
            write_new_json(path, record)
        except Exception as error:
            print(
                json.dumps(
                    {
                        "final_resources_status": "UNAVAILABLE",
                        "sidecar_error": repr(error)[:1024],
                    }
                ),
                file=sys.stderr,
            )
            if failure is None:
                raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bindings", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--tree-sha", required=True)
    parser.add_argument("--mode", choices=("baseline", "trustees"), required=True)
    parser.add_argument("--year-profile", choices=("original26",), required=True)
    parser.add_argument("--history-path", choices=(HISTORY_PATH,), required=True)
    parser.add_argument("--probe-only", action="store_true")
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest-out", required=True)
    args = parser.parse_args()
    result = run_export(args)
    print(
        json.dumps(
            {
                "complete": result["complete"],
                "probe_only": result["probe_only"],
                "parameter_count_observed": result["parameter_count_observed"],
                "parity_approved": False,
            }
        )
    )


if __name__ == "__main__":
    main()
