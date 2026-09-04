"""Trace the parameter → variable dependency map from the model.

Downstream tools (validation matching in the app, the calibration
dashboard's model-coverage page, reform classifiers) need to know which
variables a parameter path moves and which variables feed which. Static
scans of formula source miss bracket, scale, and vectorised reads; the only
exact record is what the model reads at run time. This module runs
simulations under policyengine-core's ``FullTracer`` and folds the trace
trees into two edge sets:

    readers[parameter_path] -> variables whose formula read that parameter
    consumers[variable]     -> variables whose formula read that variable

Parameter paths are recorded at the node the formula indexed, so a bracket
read ``p.base.calc(age)`` is recorded as ``gov.irs.credits.ctc.amount.base``.

Populations
-----------
``tests``      builds a simulation for every baseline YAML test (skipping
               tests that apply reforms, extensions, or inline parameter
               changes) and calculates the test's outputs. Deterministic, no
               data download, and the tests deliberately exercise every
               program and state.
``microdata``  calculates every variable over a subsample of the default
               microdata. Broad, but a formula behind ``defined_for`` only
               runs when someone in the sample qualifies.
``both``       the union.

policyengine-core quirks
------------------------
Two tracer gaps are worked around here until they are fixed upstream:

* PolicyEngine/policyengine-core#541 — the yearly ``ParameterNodeAtInstant``
  is cached before core's own tracing recast, so yearly formulas record no
  parameter reads. We flag the parameter root for tracing and clear the
  at-instant caches before calculating.
* PolicyEngine/policyengine-core#542 — ``TracingParameterNodeAtInstant``
  only records scalar leaves, so scale/bracket reads are invisible. We
  record every child that is neither a node nor a scalar leaf.

Both patches switch off once the installed core reports a version at or
above ``CORE_TRACER_FIXED_VERSION``.
"""

from __future__ import annotations

import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Callable, Iterable

import yaml

from policyengine_core import parameters as core_parameters
from policyengine_core import tracers
from policyengine_core.periods import ETERNITY
from policyengine_core.simulations import SimulationBuilder

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TESTS_ROOT = PACKAGE_ROOT / "tests" / "policy" / "baseline"
DEFAULT_OUTPUT = Path("dependency-map.json")

# First policyengine-core release with #541 and #542 fixed. None until one ships.
CORE_TRACER_FIXED_VERSION: str | None = None

# Neutralisation switches mirror every variable 1:1 and carry no reform meaning.
IGNORED_PARAMETER_PREFIXES = ("gov.abolitions.",)

Edges = tuple[dict[str, set[str]], dict[str, set[str]]]
Progress = Callable[[str], None]

_patched = False


def _version_tuple(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", text)[:3])


def core_tracer_needs_patches() -> bool:
    if CORE_TRACER_FIXED_VERSION is None:
        return True
    return _version_tuple(version("policyengine-core")) < _version_tuple(
        CORE_TRACER_FIXED_VERSION
    )


def install_tracer_patches() -> None:
    """Work around policyengine-core#542 and drop retained trace values."""
    global _patched
    if _patched:
        return
    _patched = True
    # Trace values are never read back; dropping them keeps memory flat.
    tracers.FullTracer.record_calculation_result = lambda self, value: None
    if not core_tracer_needs_patches():
        return

    original = tracers.TracingParameterNodeAtInstant.get_traced_child

    def get_traced_child(self, child, key):
        is_node = isinstance(
            child,
            (
                core_parameters.ParameterNodeAtInstant,
                core_parameters.VectorialParameterNodeAtInstant,
            ),
        )
        is_leaf = isinstance(child, core_parameters.ALLOWED_PARAM_TYPES) or hasattr(
            child, "shape"
        )
        if not is_node and not is_leaf:
            node = self.parameter_node_at_instant
            name = node._name if not isinstance(key, str) else f"{node._name}.{key}"
            self.tracer.record_parameter_access(
                name, node._instant_str, self.branch_name, None
            )
        return original(self, child, key)

    tracers.TracingParameterNodeAtInstant.get_traced_child = get_traced_child


def enable_tracing(simulation) -> None:
    """Switch tracing on, working around policyengine-core#541."""
    simulation.trace = True
    if not core_tracer_needs_patches():
        return
    root = simulation.tax_benefit_system.parameters
    root.trace = True
    root.tracer = simulation.tracer
    root.branch_name = simulation.branch_name

    def clear(node) -> None:
        cache = getattr(node, "_at_instant_cache", None)
        if cache is not None:
            cache.clear()
        children = getattr(node, "children", None)
        if isinstance(children, dict):
            for child in children.values():
                clear(child)

    clear(root)


def collect_edges(simulation, readers=None, consumers=None) -> Edges:
    """Fold a traced simulation's trees into the two edge sets."""
    readers = defaultdict(set) if readers is None else readers
    consumers = defaultdict(set) if consumers is None else consumers
    seen: set[int] = set()

    def walk(node) -> None:
        if id(node) in seen:
            return
        seen.add(id(node))
        for parameter in node.parameters:
            if not parameter.name.startswith(IGNORED_PARAMETER_PREFIXES):
                readers[parameter.name].add(node.name)
        for child in node.children:
            if child.name != node.name:
                consumers[child.name].add(node.name)
            walk(child)

    for tree in simulation.tracer.trees:
        walk(tree)
    return readers, consumers


def iter_yaml_tests(paths: Iterable[Path]):
    """Yield (file, test) for every baseline test we can trace as-is."""
    for path in paths:
        files = sorted(path.rglob("*.yaml")) if path.is_dir() else [path]
        for file in files:
            tests = yaml.safe_load(file.read_text()) or []
            if not isinstance(tests, list):
                continue
            for test in tests:
                inputs = test.get("input") or {}
                if test.get("reforms") or test.get("extensions"):
                    continue
                if any("." in key for key in inputs):
                    continue  # inline parameter change: not the baseline system
                if not test.get("output"):
                    continue
                yield file, test


def trace_yaml_tests(
    system,
    paths: Iterable[Path] = (DEFAULT_TESTS_ROOT,),
    progress: Progress | None = None,
) -> tuple[Edges, dict[str, int]]:
    install_tracer_patches()
    readers: dict[str, set[str]] = defaultdict(set)
    consumers: dict[str, set[str]] = defaultdict(set)
    stats = {"tests": 0, "failed": 0}
    for index, (file, test) in enumerate(iter_yaml_tests(paths)):
        period = test.get("period")
        try:
            builder = SimulationBuilder()
            builder.set_default_period(period)
            simulation = builder.build_from_dict(system, test.get("input") or {})
            simulation.default_calculation_period = builder.default_period
            enable_tracing(simulation)
            for output in test["output"]:
                try:
                    simulation.calculate(output, period)
                except Exception:  # noqa: BLE001 — a failing test still traced what ran
                    pass
            collect_edges(simulation, readers, consumers)
            stats["tests"] += 1
        except Exception:  # noqa: BLE001 — unbuildable situation, skip it
            stats["failed"] += 1
        if progress and index % 500 == 0:
            progress(f"  {index} tests traced ({file.relative_to(PACKAGE_ROOT)})")
    return (readers, consumers), stats


def trace_microdata(
    households: int = 2000,
    year: int = 2026,
    progress: Progress | None = None,
) -> tuple[Edges, dict[str, int]]:
    install_tracer_patches()
    from policyengine_us import Microsimulation

    simulation = Microsimulation()
    simulation = simulation.subsample(n=households, seed=0) or simulation
    enable_tracing(simulation)
    variables = simulation.tax_benefit_system.variables
    stats = {"variables": 0, "failed": 0}
    for index, name in enumerate(sorted(variables)):
        variable = variables[name]
        if variable.definition_period == ETERNITY:
            periods = [ETERNITY]
        elif variable.definition_period == "month":
            periods = [f"{year}-01"]
        else:
            periods = [year, f"{year}-01"]
        for period in periods:
            try:
                simulation.calculate(name, period)
                stats["variables"] += 1
                break
            except Exception:  # noqa: BLE001 — any formula failure just skips the variable
                continue
        else:
            stats["failed"] += 1
        if progress and index % 500 == 0:
            progress(f"  {index}/{len(variables)} variables")
    return collect_edges(simulation), stats


def merge_edges(*edge_sets: Edges) -> Edges:
    readers: dict[str, set[str]] = defaultdict(set)
    consumers: dict[str, set[str]] = defaultdict(set)
    for edge_readers, edge_consumers in edge_sets:
        for path, names in edge_readers.items():
            readers[path] |= names
        for name, users in edge_consumers.items():
            consumers[name] |= users
    return readers, consumers


def build_dependency_map(
    population: str = "tests",
    tests_root: Path = DEFAULT_TESTS_ROOT,
    households: int = 2000,
    year: int = 2026,
    progress: Progress | None = None,
) -> dict:
    from policyengine_us import CountryTaxBenefitSystem
    from policyengine_us.build_metadata import get_runtime_metadata

    edge_sets: list[Edges] = []
    populations: dict[str, dict] = {}
    started = time.time()
    if population in ("tests", "both"):
        edges, stats = trace_yaml_tests(
            CountryTaxBenefitSystem(), [tests_root], progress
        )
        edge_sets.append(edges)
        populations["tests"] = {
            "root": tests_root.relative_to(PACKAGE_ROOT).as_posix(),
            **stats,
        }
    if population in ("microdata", "both"):
        edges, stats = trace_microdata(households, year, progress)
        edge_sets.append(edges)
        populations["microdata"] = {"households": households, "year": year, **stats}
    if not edge_sets:
        raise ValueError(f"unknown population {population!r}")

    readers, consumers = merge_edges(*edge_sets)
    runtime = get_runtime_metadata()
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": {
            "package": runtime["name"],
            "version": runtime["version"],
            "gitSha": runtime["git_sha"],
            "dataBuildFingerprint": runtime["data_build_fingerprint"],
            "coreVersion": version("policyengine-core"),
        },
        "populations": populations,
        "tracingSeconds": round(time.time() - started),
        "readers": {path: sorted(names) for path, names in sorted(readers.items())},
        "consumers": {name: sorted(users) for name, users in sorted(consumers.items())},
    }


def write_dependency_map(payload: dict, output: Path = DEFAULT_OUTPUT) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, separators=(",", ":")) + "\n")
    return output


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="policyengine-us dependency-map",
        description="Trace which variables read each parameter and which variables feed which.",
    )
    parser.add_argument(
        "--population",
        choices=["tests", "microdata", "both"],
        default="tests",
    )
    parser.add_argument("--tests-root", type=Path, default=DEFAULT_TESTS_ROOT)
    parser.add_argument("--households", type=int, default=2000)
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    def progress(message: str) -> None:
        print(message, file=sys.stderr, flush=True)

    payload = build_dependency_map(
        population=args.population,
        tests_root=args.tests_root,
        households=args.households,
        year=args.year,
        progress=progress,
    )
    output = write_dependency_map(payload, args.output)
    progress(
        f"wrote {output}: {len(payload['readers'])} parameter paths, "
        f"{len(payload['consumers'])} consumed variables, "
        f"{payload['tracingSeconds']}s"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
