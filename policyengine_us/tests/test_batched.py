#!/usr/bin/env python
"""
Generic test runner that can split tests into batches for memory management.
Can be used for any test folder with configurable batch count.
"""

import subprocess
import sys
import os
import tempfile
import gc
import time
import argparse
import re
import select
import shlex
import threading
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor
from concurrent.futures import wait as futures_wait
from pathlib import Path
from typing import FrozenSet, List, Dict, Optional, Tuple
from xml.etree import ElementTree

import yaml


# policyengine-core collects both YAML suffixes
# (policyengine_core/tools/test_runner.py accepts ".yaml" and ".yml"), so any
# batch built by listing files has to list both. Enumerating only "*.yaml"
# would hand the subprocess a path list that silently omits a ".yml" test —
# invisibly, because the batch it belonged to still passes.
YAML_SUFFIXES = (".yaml", ".yml")


def yaml_files(directory: Path) -> List[Path]:
    """Every YAML test file under a directory, recursively, in a stable order."""
    return sorted(
        path for suffix in YAML_SUFFIXES for path in directory.rglob(f"*{suffix}")
    )


def root_yaml_files(directory: Path) -> List[Path]:
    """YAML test files directly in a directory, not in its subdirectories."""
    return sorted(
        path for suffix in YAML_SUFFIXES for path in directory.glob(f"*{suffix}")
    )


def count_yaml_files(directory: Path) -> int:
    """Count YAML files in a directory recursively."""
    if not directory.exists():
        return 0
    return len(yaml_files(directory))


def batch_cost(batch_paths: List[str]) -> int:
    """Estimated batch cost: total YAML files across the batch's paths."""
    return sum(
        count_yaml_files(Path(p)) if Path(p).is_dir() else 1 for p in batch_paths
    )


# --- Reform-combo memory weighting ------------------------------------------
#
# policyengine-core's YAML runner builds one full deep copy of the
# tax-benefit system per distinct (reforms, parametric-overrides)
# combination a test case requests, and caches it for the life of the
# subprocess — the cache is never evicted. Peak subprocess RSS is therefore
# driven by how many DISTINCT combos a batch accumulates, not by how many
# files or cases it runs. Calibrated against 46 contrib/states batches on
# 16 GB ubuntu-latest runners (CI run 28756084246, 2026-07-05):
#
#   peak_rss_mb ≈ 1450 + 1450 * structural_combos
#
# with the batch that accumulated 11 combos peaking at 15.2 GB and killing
# sibling runs ("The runner has received a shutdown signal").

# One structural combo (a `reforms:` entry, with or without parameter
# overrides) ≈ 1.45 GB of permanently-resident memory.
STRUCTURAL_COMBO_WEIGHT = 1.0
# Parametric-only overrides skip the reform apply and share more of the
# parameter tree; historical RI sweeps measured ~0.2-0.3 GB per combo.
PARAM_ONLY_COMBO_WEIGHT = 0.25
# 1.45 + 1.45 * 5 ≈ 8.7 GB predicted peak — just over half the 16 GB
# runner, leaving the other half as headroom for future tests.
MAX_BATCH_COMBO_WEIGHT = 5.0

# A combo key mirrors policyengine-core's tax-benefit-system cache key:
# the case's reforms plus its dotted-path parameter overrides (values
# included — each distinct value set is a separate cached system).
ComboKey = Tuple[Tuple[str, ...], FrozenSet[Tuple[str, str]]]


def file_reform_combos(yaml_file: Path) -> FrozenSet[ComboKey]:
    """Distinct (reforms, parametric-overrides) combos a test file triggers.

    Unparseable or non-test YAML contributes no weight; the real test run
    surfaces any genuine syntax error.
    """
    try:
        cases = yaml.safe_load(yaml_file.read_text())
    except (OSError, yaml.YAMLError):
        return frozenset()
    if not isinstance(cases, list):
        return frozenset()
    combos = set()
    for case in cases:
        if not isinstance(case, dict):
            continue
        reforms = case.get("reforms")
        if isinstance(reforms, list):
            reforms_key = tuple(str(r) for r in reforms)
        elif reforms is None:
            reforms_key = ()
        else:
            reforms_key = (str(reforms),)
        overrides = frozenset(
            (key, repr(value))
            for key, value in (case.get("input") or {}).items()
            if isinstance(key, str) and "." in key
        )
        if reforms_key or overrides:
            combos.add((reforms_key, overrides))
    return frozenset(combos)


def combo_weight(combos: FrozenSet[ComboKey]) -> float:
    """Memory weight of a set of combos, in structural-combo units."""
    structural = sum(1 for reforms, _ in combos if reforms)
    param_only = len(combos) - structural
    return structural * STRUCTURAL_COMBO_WEIGHT + param_only * PARAM_ONLY_COMBO_WEIGHT


def pack_files_by_combo_weight(files: List[Path]) -> List[List[str]]:
    """Pack files into batches so no subprocess exceeds the combo budget.

    Greedy in sorted order: a file joins the current batch if the batch's
    DISTINCT combo set (mirroring the runner's cache, so identical combos
    across files count once) stays within MAX_BATCH_COMBO_WEIGHT. A single
    file over the budget gets its own batch — the runner cannot split below
    file granularity — with a loud warning; the code-health test
    test_reform_combo_budget.py fails such files at authoring time.
    """
    batches: List[List[str]] = []
    current: List[str] = []
    current_combos: set = set()
    for file in files:
        file_combos = file_reform_combos(file)
        merged = current_combos | file_combos
        if current and combo_weight(frozenset(merged)) > MAX_BATCH_COMBO_WEIGHT:
            batches.append(current)
            current = []
            current_combos = set()
            merged = set(file_combos)
        current.append(str(file))
        current_combos = merged
        file_weight = combo_weight(file_combos)
        if file_weight > MAX_BATCH_COMBO_WEIGHT:
            print(
                f"WARNING: {file} alone carries reform-combo weight "
                f"{file_weight:.2f} (> {MAX_BATCH_COMBO_WEIGHT}); it gets a "
                f"dedicated subprocess but should be split into smaller "
                f"files (see tests/code_health/test_reform_combo_budget.py)."
            )
            batches.append(current)
            current = []
            current_combos = set()
    if current:
        batches.append(current)
    return batches


def _read_vm_hwm_mb(pid: int) -> Optional[float]:
    """Peak RSS (VmHWM high-water mark) of a live process, in MB.

    Linux-only: /proc does not exist on macOS, and the entry disappears
    once the pid is reaped — both cases return None.
    """
    try:
        with open(f"/proc/{pid}/status") as status_file:
            for line in status_file:
                if line.startswith("VmHWM:"):
                    # Format: "VmHWM:    123456 kB"
                    return int(line.split()[1]) / 1024
    except (OSError, ValueError, IndexError):
        return None
    return None


def _format_rss(peak_rss_mb: Optional[float]) -> str:
    return f"{peak_rss_mb:.0f} MB" if peak_rss_mb is not None else "n/a"


def subdir_batches(subdir: Path) -> List[List[str]]:
    """One batch per subdir unless its distinct combos exceed the budget.

    A proposal folder normally shares one subprocess so files that request
    the same reform share one cached system. Once the folder's DISTINCT
    combos exceed MAX_BATCH_COMBO_WEIGHT that shared subprocess is exactly
    what exhausts the runner: congress/tlaib carries weight 8.25 and peaked
    at 15.0 GB on the 16 GB runner at main (CI run 34637166889), leaving no
    headroom, and a branch run of the same batch produced no output for 39
    minutes before CI killed it. Pack such a folder's files by combo weight
    instead.
    """
    files = yaml_files(subdir)
    if not files:
        # Python-only folders are covered by the dedicated Python suites.
        return []
    combos: set = set()
    for file in files:
        combos |= set(file_reform_combos(file))
    if combo_weight(frozenset(combos)) <= MAX_BATCH_COMBO_WEIGHT:
        return [[str(subdir)]]
    return pack_files_by_combo_weight(files)


def split_into_batches(
    base_path: Path,
    num_batches: int,
    exclude: List[str] = None,
    mode: str = "auto",
) -> List[List[str]]:
    """
    Split test directories into specified number of batches.
    Special handling for baseline tests to separate states.
    Special handling for contrib tests to divide by folder count.

    Args:
        base_path: Path to the test directory
        num_batches: Number of batches to split into
        exclude: List of directory names to exclude (for contrib tests)
        mode: Batching mode. "auto" (default) uses the per-path heuristics
            below. "per-subdir" runs each immediate subdir as its own batch
            (packed by reform-combo weight when it exceeds the budget) with
            loose yamls collected into a trailing batch. "per-file"
            runs every yaml (recursively) as its own batch.
    """
    if exclude is None:
        exclude = []

    # Explicit modes — bypass the per-path auto heuristics so new files
    # added to the target auto-route without a Makefile edit.
    if mode == "per-file":
        return [[str(f)] for f in yaml_files(base_path)]

    if mode == "per-subdir":
        subdirs = sorted(
            item
            for item in base_path.iterdir()
            if item.is_dir() and item.name not in exclude
        )
        root_files = root_yaml_files(base_path)
        batches = [batch for s in subdirs for batch in subdir_batches(s)]
        if root_files:
            batches.append([str(f) for f in root_files])
        return batches

    # Special handling for contrib tests - one batch per heavy folder.
    # Only apply to policy/contrib (structural tests), not baseline/contrib.
    #
    # Prior grouping (3 folders per batch) pushed peak memory to ~8-9 GB
    # per subprocess, which OOMs the 16 GB ubuntu-latest runner once
    # policyengine-core 3.24+ overhead is added, surfacing as
    # "The runner has received a shutdown signal" mid-batch. Giving each
    # heavy folder its own batch keeps peaks under ~5 GB and eliminates
    # the intermittent failures without reducing total coverage.
    if str(base_path).endswith("policy/contrib"):
        # Heavy folders each get their own batch (~3-5 GB peak each) so
        # a single subprocess doesn't exceed the 16 GB runner cap.
        HEAVY = {
            "federal",
            "harris",
            "treasury",
            "ctc",
            "snap_ea",
            "ubi_center",
            "deductions",
            "aca",
            "snap",
            "tax_exempt",
            "eitc",
            "crfb",
            "congress",
        }
        # Some folders contain individual YAMLs that are each expensive
        # enough to need their own subprocess.
        PER_FILE = {"refundable_credit_conversion"}

        subdirs = sorted(
            item
            for item in base_path.iterdir()
            if item.is_dir() and item.name not in exclude
        )
        root_files = root_yaml_files(base_path)

        # One batch per file for per-file folders, then one batch per
        # heavy subdir (if present).
        batches = [
            [str(file)]
            for subdir in subdirs
            if subdir.name in PER_FILE
            for file in yaml_files(subdir)
        ]
        batches += [[str(subdir)] for subdir in subdirs if subdir.name in HEAVY]

        # Catch-all batch for everything else — light subdirs and root
        # yaml files. Auto-collects any newly added folders/files so
        # they're exercised without extra config.
        light_paths = [
            str(subdir)
            for subdir in subdirs
            if subdir.name not in HEAVY and subdir.name not in PER_FILE
        ] + [str(f) for f in root_files]
        if light_paths:
            batches.append(light_paths)

        return batches

    # Special handling for contrib/states — pack each state's files into
    # batches capped by reform-combo weight (see the weighting block at the
    # top of this file). Folder-per-batch with a hand-maintained heavy-state
    # list OOM'd within a day of tuning: two merged PRs added reform files
    # to 13 state folders and the GA batch silently grew from 3 to 11
    # distinct combos (15.2 GB peak on a 16 GB runner, CI run 28756084246).
    # Weight-capped packing splits any folder automatically as combos
    # accumulate, so new reform tests self-balance instead of re-breaking
    # the layout. States are never mixed into one batch, keeping failures
    # attributable; light states still run as a single subprocess.
    if str(base_path).endswith("contrib/states"):
        subdirs = sorted([item for item in base_path.iterdir() if item.is_dir()])
        batches = []
        for subdir in subdirs:
            batches.extend(pack_files_by_combo_weight(yaml_files(subdir)))

        # Also include any root-level YAML files as trailing batches
        root_files = root_yaml_files(base_path)
        if root_files:
            batches.extend(pack_files_by_combo_weight(root_files))

        return batches if batches else [[str(base_path)]]

    # Special handling for reform tests - one batch per file. Reforms are
    # force-applied and deepcopy the full parameter tree (~5.5 GB peak/file
    # for ctc_linear_phase_out and winship, measured); running all files in
    # one subprocess stacks past the 16 GB runner cap → "runner received a
    # shutdown signal". A fresh subprocess per file frees each peak between
    # files.
    if "reform" in str(base_path):
        return [[str(f)] for f in yaml_files(base_path)]

    # Special handling for states directory - support excluding specific states
    # and splitting into multiple sequential batches for memory management
    if str(base_path).endswith("gov/states"):
        subdirs = sorted(
            [
                item
                for item in base_path.iterdir()
                if item.is_dir() and item.name not in exclude
            ]
        )
        # Root-level YAML files (e.g. cross-state filing-status test) are
        # state-agnostic and would be invisible to subdir-based batching
        # otherwise — collect them into a dedicated trailing batch.
        root_files = root_yaml_files(base_path)

        if not subdirs and not root_files:
            return []
        # Split into num_batches sequential groups
        if num_batches > 1:
            chunk_size = len(subdirs) // num_batches
            remainder = len(subdirs) % num_batches
            batches = []
            start = 0
            for i in range(num_batches):
                end = start + chunk_size + (1 if i < remainder else 0)
                batch = [str(s) for s in subdirs[start:end]]
                if batch:
                    batches.append(batch)
                start = end
            if root_files:
                batches.append([str(f) for f in root_files])
            return batches
        batches = []
        if subdirs:
            batches.append([str(subdir) for subdir in subdirs])
        if root_files:
            batches.append([str(f) for f in root_files])
        return batches

    # Special handling for baseline tests
    if "baseline" in str(base_path) and str(base_path).endswith("baseline"):
        states_path = base_path / "gov" / "states"

        # If --exclude states, skip states and run everything else
        # Split into memory-aware batches to prevent OOM on CI (~7 GB limit)
        # Measured peak memory per gov/ subfolder (individual runs):
        #   irs: 4.4 GB, ssa: 4.0 GB, simulation: 4.0 GB,
        #   usda: 3.0 GB, hhs: 2.7 GB, local: 2.3 GB,
        #   others: ~1.3-1.7 GB each
        if "states" in exclude:
            gov_path = base_path / "gov"

            # One batch per heavy gov/ folder (~3-4 GB peak each) so no
            # subprocess exceeds ~5 GB. Grouping previously-paired folders
            # (usda+hhs) pushed peak memory past the 16 GB runner cap once
            # policyengine-core 3.24+ overhead landed.
            HEAVY = ["irs", "ssa", "simulation", "usda", "hhs"]

            def collect_gov_paths(folder_names):
                """Collect paths for specific gov/ subfolders."""
                paths = []
                for name in folder_names:
                    p = gov_path / name
                    if p.exists():
                        paths.append(str(p))
                return paths

            # Collect remaining gov/ subfolders and files
            remaining = []
            heavy_set = set(HEAVY)
            for gov_item in gov_path.iterdir():
                if gov_item.is_dir():
                    if gov_item.name not in heavy_set and gov_item.name != "states":
                        remaining.append(str(gov_item))
                elif gov_item.suffix in YAML_SUFFIXES:
                    remaining.append(str(gov_item))

            # Add non-gov directories and root YAML files
            for item in base_path.iterdir():
                if item.is_dir():
                    if item.name in ["household", "contrib", "gov"]:
                        continue
                    remaining.append(str(item))
                elif item.suffix in YAML_SUFFIXES:
                    remaining.append(str(item))

            # Build batches (only include non-empty ones)
            batches = []
            for folder_name in HEAVY:
                paths = collect_gov_paths([folder_name])
                if paths:
                    batches.append(paths)
            if remaining:
                batches.append(remaining)

            return batches

    # Default: honor num_batches and exclude generically. The cheapest
    # common case (no chunking, no exclusion) returns the base_path as a
    # single batch so policyengine-core walks the tree once. Otherwise we
    # enumerate explicit paths — necessary because the test runner has no
    # way to skip excluded subpaths on its own, and because splitting into
    # multiple subprocesses requires discrete path lists.
    if num_batches <= 1 and not exclude:
        return [[str(base_path)]]

    if exclude:
        # Exclude applies to immediate children by name (same semantics as
        # the special-branch excludes above). Previously, `--exclude` in
        # the default branch was silently ignored, causing duplicated
        # work — e.g. `ny --exclude tax` still re-ran every `tax/*` test.
        paths = sorted(
            str(item)
            for item in base_path.iterdir()
            if (item.is_dir() or item.suffix in YAML_SUFFIXES)
            and item.name not in exclude
        )
    else:
        paths = [str(f) for f in yaml_files(base_path)]

    if not paths:
        return []

    if num_batches <= 1:
        return [paths]

    chunk_size = len(paths) // num_batches
    remainder = len(paths) % num_batches
    batches = []
    start = 0
    for i in range(num_batches):
        end = start + chunk_size + (1 if i < remainder else 0)
        chunk = paths[start:end]
        if chunk:
            batches.append(chunk)
        start = end
    return batches


# pytest exits 5 when a path collects no tests (see pytest.ExitCode).
PYTEST_NO_TESTS_COLLECTED = 5
# How long a child gets to die after being asked to, before it is killed.
TERMINATE_GRACE_SECONDS = 5
# Budget for one subprocess, enforced inside the monitoring loop below. A
# batch the memory budget continues in fresh subprocesses gets a fresh budget
# for each part (see run_batch).
BATCH_TIMEOUT_SECONDS = 1800
# How long the runner may take to hand back a status after printing its
# summary. That gap is pytest's own session-finish hooks and unconfigure, not
# the slow interpreter teardown described below, which happens after the
# marker: measured, the marker arrives in the same read as the summary line.
# This is deliberately generous, and exists only so a runner that stops
# responding right at the end is reported instead of hanging the job.
MARKER_GRACE_SECONDS = 300

# The runner's process exit status is not reachable in bounded time. Once
# policyengine-core's pytest.main() returns, interpreter teardown frees the
# tax-benefit systems the run cached, which is slow: measured on this suite, a
# single small state took 18.2s to exit after printing its summary, and the
# large state batches took over 30s. That is why the runner is terminated as
# soon as it reports rather than waited out - and why its status used to be
# discarded along with it, leaving the printed summary as the only evidence.
#
# So ask for the status at the only moment it is both known and free: run the
# command through a shim that writes pytest's own return value to stdout the
# instant pytest.main() hands it back, before any teardown. Measured at the
# same moment as the summary line, so this costs no wall clock, and the child
# is still terminated exactly as promptly as before.
BATCH_EXIT_MARKER = "__POLICYENGINE_BATCH_EXIT__"

# Memory accumulates across the YAML files one subprocess runs: household's 15
# root files peaked at 13.3 GB together (local peak footprint, 2026-10-14, within
# 1% of CI's VmHWM on the batches compared), yet none passed 6.2 GB alone, and
# CI's household and gov/hhs batches each reached 15.1 GB on the 16 GB runner.
# Any fixed batch layout therefore outgrows the runner as tests are added. Instead, after each file the child checks its own peak memory and,
# once past this budget, hands the files it has not started to a fresh
# subprocess (run_batch continues them). The next file starts below the budget,
# so a subprocess peaks at about the budget plus one file's growth. A file that
# alone exceeds the budget still runs whole. Set the variable to override it,
# e.g. 0 for one file per subprocess.
MEMORY_BUDGET_MB = 8000
MEMORY_BUDGET_ENV = "POLICYENGINE_BATCH_MEMORY_BUDGET_MB"
REMAINDER_ENV = "POLICYENGINE_BATCH_REMAINDER"

# POLICYENGINE_BATCH_WORKERS lets several batch subprocesses share a runner
# while its memory allows; it overrides --workers. (A plain --workers N, as
# the partners target uses for its small batches, still runs N at once.) A
# 16 GB, 4-CPU CI runner running one subprocess is about 25% busy, but two
# fixed subprocesses ran it out of memory (fork runs 38687143268 and
# 38689387981: a runner shutdown in the crfb group in each, and 77-296 MB
# left in the contrib states groups). So with the variable above 1, memory
# decides how many run:
# - another subprocess starts only while the runner has ADMIT_MB available,
#   and at most one starts per ADMIT_STAGGER_SECONDS, since a new one takes
#   that long to load the model; one subprocess may always run;
# - a subprocess hands off its unstarted files at a file boundary (as for the
#   memory budget) once the runner has less than FLOOR_MB available, and the
#   remainder waits for admission;
# - if the runner falls below EVICT_MB mid-file, the newest of two or more
#   subprocesses is stopped and its files rerun alone once the others finish;
# - batches are split, whole files only, until there is one per worker.
# Where available memory cannot be read (off Linux), one subprocess runs at a
# time. With two workers the 20 Baseline and Contrib groups averaged 345
# runner-minutes per fork run against 508 with one (32% fewer over three runs;
# 33% over 38689387981 and 38710504296, which ran this eviction protocol),
# passed the same 34,794 cases, and never ran a runner out of memory. Three or
# four workers were no faster, because memory, not CPU, runs out first.
WORKERS_ENV = "POLICYENGINE_BATCH_WORKERS"
FLOOR_ENV = "POLICYENGINE_BATCH_MEMORY_FLOOR_MB"
ADMIT_MB = 6000
FLOOR_MB = 4000
EVICT_MB = 2000
ADMIT_STAGGER_SECONDS = 20


def available_mb() -> Optional[float]:
    """The runner's MemAvailable in MB, or None off Linux."""
    try:
        with open("/proc/meminfo") as meminfo:
            for line in meminfo:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) / 1024
    except (OSError, ValueError, IndexError):
        return None
    return None


# Child-side half of the memory budget. policyengine-core calls
# pytest.main(..., plugins=[...]) through the pytest module, so wrapping it
# adds this plugin without changing Core.
MEMORY_GUARD = """
budget_mb = os.environ.get("POLICYENGINE_BATCH_MEMORY_BUDGET_MB")
remainder_path = os.environ.get("POLICYENGINE_BATCH_REMAINDER")
floor_mb = os.environ.get("POLICYENGINE_BATCH_MEMORY_FLOOR_MB")
if budget_mb and remainder_path:
    import pytest

    def runner_available_mb():
        try:
            with open("/proc/meminfo") as meminfo:
                for line in meminfo:
                    if line.startswith("MemAvailable:"):
                        return int(line.split()[1]) / 1024
        except OSError:
            pass
        return None

    def peak_mb():
        try:
            with open("/proc/self/status") as status:
                for line in status:
                    if line.startswith("VmHWM:"):
                        return int(line.split()[1]) / 1024
        except OSError:
            pass
        if sys.platform == "darwin":
            # ru_maxrss leaves out compressed memory, which reads 2-3x low on
            # these suites. RUSAGE_INFO_V4 word 30 is the lifetime peak physical
            # footprint that /usr/bin/time -l reports.
            try:
                import ctypes

                info = (ctypes.c_uint64 * 64)()
                libc = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
                if libc.proc_pid_rusage(os.getpid(), 4, ctypes.byref(info)) == 0:
                    return info[30] / 2**20
            except (OSError, AttributeError):
                pass
        import resource

        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # ru_maxrss is bytes on macOS and kilobytes on Linux.
        return peak / 2**20 if sys.platform == "darwin" else peak / 1024

    class MemoryBudget:
        @pytest.hookimpl(wrapper=True)
        def pytest_runtest_protocol(self, item, nextitem):
            result = yield
            # Only stop between files, so every file runs whole in one process.
            if nextitem is None or nextitem.path == item.path:
                return result
            peak = peak_mb()
            low = runner_available_mb() if floor_mb else None
            if low is not None and low >= float(floor_mb):
                low = None
            if peak < float(budget_mb) and low is None:
                return result
            items = item.session.items
            remaining = list(
                dict.fromkeys(str(later.path) for later in items[items.index(nextitem) :])
            )
            with open(remainder_path, "w") as handle:
                handle.write("\\n".join(remaining))
            reason = (
                "peak %.0f MB" % peak
                if low is None
                else "runner available %.0f MB (own peak %.0f MB)" % (low, peak)
            )
            pytest.exit(
                "memory budget: %s after %s; %d files continue in a "
                "fresh subprocess" % (reason, item.path.name, len(remaining)),
                returncode=1 if item.session.testsfailed else 0,
            )

    run_pytest = pytest.main

    def main(args=None, plugins=None, **kwargs):
        return run_pytest(args, [*(plugins or []), MemoryBudget()], **kwargs)

    pytest.main = main
"""

RUNNER_SHIM = f"""
import os
import runpy
import sys

# Python suites run separately; directory batches must collect only YAML.
# Set this in the child so the later Python step keeps its normal collection.
os.environ["PYTEST_ADDOPTS"] = (
    os.environ.get("PYTEST_ADDOPTS", "") + " --ignore-glob=*.py"
)
{MEMORY_GUARD}
code = 0
try:
    runpy.run_module(
        "policyengine_core.scripts.policyengine_command", run_name="__main__"
    )
except SystemExit as requested:
    code = requested.code
sys.stdout.write("\\n{BATCH_EXIT_MARKER} %s\\n" % (0 if code is None else code))
sys.stdout.flush()
sys.exit(code)
"""

BATCH_EXIT_PATTERN = re.compile(rf"{BATCH_EXIT_MARKER} (-?\d+)")


def build_test_command(test_paths: List[str], python_exe: str) -> List[str]:
    """The policyengine-core command one batch runs in its own subprocess.

    `python -c` stops consuming options after the program text, so everything
    after RUNNER_SHIM reaches policyengine_command's own argument parser
    unchanged.
    """
    return (
        [python_exe, "-c", RUNNER_SHIM, "test"] + test_paths + ["-c", "policyengine_us"]
    )


def describe_exit_status(returncode: Optional[int]) -> str:
    """Human-readable form of a batch subprocess's exit status."""
    if returncode is None:
        return "no exit status (killed after it stopped responding)"
    if returncode == 0:
        return "exit 0"
    if returncode < 0:
        return f"killed by signal {-returncode}"
    if returncode == PYTEST_NO_TESTS_COLLECTED:
        return f"exit {returncode} (pytest collected no tests)"
    return f"exit {returncode}"


def batch_status(returncode: Optional[int]) -> str:
    """Batch outcome, decided by the runner's exit status and nothing else.

    policyengine-core's `test` command is `sys.exit(pytest.main(...))`
    (scripts/run_test.py), so the status is pytest's own ExitCode and only 0 is
    a pass. Reading the printed summary instead loses every outcome pytest does
    not express as a failure count:

    * "1 passed, 1 error" prints no failed count at all, so the old parse read
      an errored batch as success while the child exited 1.
    * 2 (interrupted) prints a count for whatever ran before the interrupt and
      no failure count, which the old parse also read as success: under
      policyengine-core's argv, a session whose second test raises
      KeyboardInterrupt exits 2 beneath "1 passed in 0.10s" (measured).
    * 3 and 4 (internal error, usage error) print no summary count at all, so
      the old parse fell through to a status it had already discarded.
    * 5 (no tests collected) is a failure *for this runner*. It differs from
      run_selective_tests.py, which skips 5 deliberately: that runner selects
      paths from a changed-file list, where a changed test helper legitimately
      collects nothing. This runner enumerates the YAML suite itself, so a
      batch that collects nothing means the suite or this enumeration is
      broken — a result to report, not to pass over.
    * None means the child never reported a status, having been killed after
      it stopped responding. An unreported batch is not a passing batch.
    """
    return "passed" if returncode == 0 else "failed"


def junit_report_path() -> Optional[str]:
    """The --junitxml file PYTEST_ADDOPTS asks every part to write, if any."""
    tokens = shlex.split(os.environ.get("PYTEST_ADDOPTS", ""))
    path = None
    for i, token in enumerate(tokens):
        for flag in ("--junitxml", "--junit-xml"):
            if token.startswith(flag + "="):
                path = token.split("=", 1)[1]
            elif token == flag and i + 1 < len(tokens):
                path = tokens[i + 1]
    return path


def report_mtime(path: Optional[str]) -> Optional[int]:
    try:
        return os.stat(path).st_mtime_ns if path else None
    except FileNotFoundError:
        return None


class Admission:
    """Starts batch subprocesses only while the runner has memory for them.

    One subprocess may always run, so a run never stalls. An evicted part
    reruns exclusively: no new subprocess starts while it waits or runs.
    """

    def __init__(self, admit_mb: float = ADMIT_MB, evict_mb: float = EVICT_MB):
        self.admit_mb = admit_mb
        self.evict_mb = evict_mb
        self.cond = threading.Condition()
        self.running: Dict[int, list] = {}
        self.evicted: set = set()
        self.pending_exclusive: set = set()
        self.exclusive_waiting = 0
        self.exclusive_holder: Optional[int] = None
        self.last_admit = 0.0
        self.waits = 0
        self.evictions = 0
        self.stopped = False
        threading.Thread(target=self.watch, daemon=True).start()

    def may_admit(self) -> bool:
        if (
            self.exclusive_holder is not None
            or self.exclusive_waiting
            or self.pending_exclusive
        ):
            return False
        if not self.running:
            return True
        if time.time() - self.last_admit < ADMIT_STAGGER_SECONDS:
            return False
        avail = available_mb()
        return avail is not None and avail >= self.admit_mb

    def acquire(self, exclusive: bool) -> None:
        ident = threading.get_ident()
        with self.cond:
            if exclusive:
                self.exclusive_waiting = self.exclusive_waiting + 1
                self.pending_exclusive.discard(ident)
                while self.running or self.exclusive_holder is not None:
                    self.cond.wait(1)
                self.exclusive_waiting = self.exclusive_waiting - 1
                self.exclusive_holder = ident
            elif not self.may_admit():
                self.waits = self.waits + 1
                while not self.may_admit():
                    self.cond.wait(1)
            self.running[ident] = [None, time.time()]
            self.last_admit = time.time()

    def started(self, process) -> None:
        with self.cond:
            entry = self.running.get(threading.get_ident())
            if entry is not None:
                entry[0] = process

    def finished(self) -> None:
        """The part reported or exited: stop treating it as live."""
        self.started(None)

    def forget(self) -> None:
        """Drop this thread's rerun reservation, if it will not rerun."""
        with self.cond:
            self.pending_exclusive.discard(threading.get_ident())
            self.cond.notify_all()

    def release(self) -> bool:
        ident = threading.get_ident()
        with self.cond:
            self.running.pop(ident, None)
            evicted = ident in self.evicted
            self.evicted.discard(ident)
            if self.exclusive_holder == ident:
                self.exclusive_holder = None
            self.cond.notify_all()
        return evicted

    def watch(self) -> None:
        while not self.stopped:
            time.sleep(0.2)
            avail = available_mb()
            if avail is None or avail >= self.evict_mb:
                continue
            with self.cond:
                live = [
                    (entry[1], ident, entry[0])
                    for ident, entry in self.running.items()
                    if entry[0] is not None and ident not in self.evicted
                ]
                if len(live) < 2:
                    continue
                _, ident, process = max(live, key=lambda item: item[0])
                self.evicted.add(ident)
                self.pending_exclusive.add(ident)
                self.evictions = self.evictions + 1
            print(
                f"[memory] runner available {avail:.0f} MB < {self.evict_mb:.0f} MB "
                f"with {len(live)} subprocesses; stopping the newest and "
                "rerunning its files alone",
                flush=True,
            )
            try:
                process.kill()
            except OSError:
                pass
            time.sleep(2)


ADMISSION: Optional[Admission] = None


def fill_workers(batches: List[List[str]], workers: int) -> List[List[str]]:
    """Split batches, whole files only, until there is one per worker."""
    if not batches:
        return batches
    expanded = []
    for batch in batches:
        files = [
            str(f)
            for p in batch
            for f in (yaml_files(Path(p)) if Path(p).is_dir() else [Path(p)])
        ]
        expanded.append(files or list(batch))
    splittable = [
        len(b) > 1 and all(p.endswith(YAML_SUFFIXES) for p in b) for b in expanded
    ]
    while len(expanded) < workers and any(splittable):
        largest = max(
            (i for i in range(len(expanded)) if splittable[i]),
            key=lambda i: len(expanded[i]),
        )
        files = expanded[largest]
        half = len(files) // 2
        expanded[largest : largest + 1] = [files[:half], files[half:]]
        splittable[largest : largest + 1] = [half > 1, len(files) - half > 1]
    return expanded


def run_batch(
    test_paths: List[str],
    batch_name: str,
    stream: bool = True,
    command: Optional[List[str]] = None,
) -> Dict:
    """Run a batch, continuing past the memory budget in fresh subprocesses.

    Each part runs through run_subprocess. A part that reaches
    MEMORY_BUDGET_MB between files (or, when subprocesses share the runner,
    finds less than FLOOR_MB available) writes the files it has not started to
    a remainder file and exits; they continue in the next part. A part stopped
    mid-file for runner memory is discarded and rerun alone. The batch passes
    only if every part passes. Each part rewrites an inherited --junitxml file,
    so the parts' suites are merged back into it.
    """
    budget = os.environ.get(MEMORY_BUDGET_ENV, str(MEMORY_BUDGET_MB))
    report = junit_report_path()
    suites: List[ElementTree.Element] = []
    parts: List[Dict] = []
    paths = test_paths
    exclusive = False
    discarded = ""
    while paths:
        handle, remainder = tempfile.mkstemp(prefix="batch-remainder-")
        os.close(handle)
        os.unlink(remainder)
        name = batch_name if not parts else f"{batch_name} (part {len(parts) + 1})"
        env = dict(os.environ, **{MEMORY_BUDGET_ENV: budget, REMAINDER_ENV: remainder})
        if ADMISSION is not None:
            env[FLOOR_ENV] = str(FLOOR_MB)
        written = report_mtime(report)
        if ADMISSION is not None:
            ADMISSION.acquire(exclusive)
        try:
            part = run_subprocess(paths, name, stream, command, env)
        finally:
            evicted = ADMISSION.release() if ADMISSION is not None else False
        if evicted and not part.get("reported"):
            note = (
                f"    [memory] {name} stopped mid-file for runner memory; "
                f"rerunning its {batch_cost(paths)} files alone"
            )
            if stream:
                print(note, flush=True)
            discarded = discarded + part["output"] + note + "\n"
            if os.path.exists(remainder):
                os.unlink(remainder)
            exclusive = True
            continue
        if evicted:
            # Stopped only after it reported: keep its result.
            ADMISSION.forget()
        exclusive = False
        parts.append(part)
        command = None
        if report_mtime(report) not in (None, written):
            suites.extend(ElementTree.parse(report).getroot().iter("testsuite"))
        try:
            with open(remainder) as handle_in:
                paths = [line for line in handle_in.read().splitlines() if line]
            os.unlink(remainder)
        except FileNotFoundError:
            paths = []
        if paths:
            limit = f"Memory budget ({budget} MB)"
            if ADMISSION is not None:
                limit = f"{limit} or runner floor ({FLOOR_MB} MB available)"
            note = (
                f"    {limit} reached; continuing "
                f"{len(paths)} files in a fresh subprocess"
            )
            if stream:
                print(note, flush=True)
            else:
                parts[-1]["output"] = parts[-1]["output"] + note + "\n"
    if len(parts) > 1 and suites:
        merged = ElementTree.Element("testsuites")
        merged.extend(suites)
        ElementTree.ElementTree(merged).write(
            report, encoding="utf-8", xml_declaration=True
        )
    failed = [part for part in parts if part["status"] != "passed"]
    peaks = [part["peak_rss_mb"] for part in parts if part["peak_rss_mb"] is not None]
    return {
        "elapsed": sum(part["elapsed"] for part in parts),
        "status": failed[0]["status"] if failed else "passed",
        "returncode": failed[0]["returncode"] if failed else 0,
        "peak_rss_mb": max(peaks) if peaks else None,
        "parts": len(parts),
        "output": discarded + "".join(part["output"] for part in parts),
    }


def run_subprocess(
    test_paths: List[str],
    batch_name: str,
    stream: bool = True,
    command: Optional[List[str]] = None,
    env: Optional[Dict[str, str]] = None,
) -> Dict:
    """Run a batch of tests in an isolated subprocess.

    With stream=True output is echoed to stdout in real time (sequential
    mode). With stream=False output is buffered and returned under the
    "output" key so a concurrent caller can print the whole batch
    atomically once it finishes.
    """

    python_exe = sys.executable

    buf: List[str] = []

    def emit(text: str, end: str = "\n") -> None:
        if stream:
            print(text, end=end, flush=True)
        else:
            buf.append(text + end)

    start_time = time.time()
    last_output_time = start_time
    last_heartbeat_time = start_time
    heartbeat_interval = 30
    peak_rss_mb = None
    last_rss_sample = 0.0

    # Build command - direct policyengine-core with timeout protection.
    # `command` is an injection point for the code-health tests, which drive a
    # real subprocess with scripted output and exit statuses.
    cmd = command or build_test_command(test_paths, python_exe)

    emit(f"    Running {batch_name}...")
    emit(f"    Paths: {len(test_paths)} items")
    emit("")

    # Use Popen for more control over process lifecycle
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
        env=env,
    )
    if ADMISSION is not None:
        ADMISSION.started(process)

    def sample_rss() -> None:
        # VmHWM is monotonic, so keeping only the latest reading preserves
        # the peak; readings stop (None) once the pid is reaped or off-Linux.
        nonlocal peak_rss_mb, last_rss_sample
        rss = _read_vm_hwm_mb(process.pid)
        if rss is not None:
            peak_rss_mb = rss
        last_rss_sample = time.time()

    try:
        test_completed = False
        summary_reported_pass = False
        abandoned: Optional[str] = None
        reported_returncode: Optional[int] = None
        output_lines = []
        output_text = ""

        summary_at: Optional[float] = None

        def stop_process() -> None:
            """End a child, whether or not it told us how it finished."""
            process.terminate()
            try:
                process.wait(timeout=TERMINATE_GRACE_SECONDS)
            except subprocess.TimeoutExpired:
                emit("    Force killing process...")
                process.kill()
                process.wait()

        def overdue() -> Optional[str]:
            """Why this batch should stop being waited on, if it should.

            The monitoring loop is otherwise unbounded, in this revision and
            the one before it: it ends only when the child exits or reports,
            and the 30-minute budget below it was only ever consulted after
            the child had already gone. Enforce that budget here, where it can
            fire, and bound the window this file opened by reading the status
            from the runner instead of terminating a second after its summary.
            """
            now = time.time()
            if now - start_time >= BATCH_TIMEOUT_SECONDS:
                return "timeout"
            if summary_at is not None and now - summary_at >= MARKER_GRACE_SECONDS:
                return "unreported"
            return None

        # Monitor output line by line
        while True:
            ready, _, _ = select.select([process.stdout], [], [], 0.1)
            if not ready:
                # Sample before poll(): poll() reaps the child, after which
                # /proc/<pid>/status is gone.
                sample_rss()
                poll_result = process.poll()
                if poll_result is not None:
                    # Process terminated
                    if ADMISSION is not None:
                        ADMISSION.finished()
                    break
                give_up = overdue()
                if give_up is not None:
                    abandoned = give_up
                    emit(
                        "\n    ⏱️ "
                        + (
                            "Timeout"
                            if give_up == "timeout"
                            else f"No status {MARKER_GRACE_SECONDS}s after the summary"
                        )
                        + " - terminating process..."
                    )
                    stop_process()
                    break
                now = time.time()
                # In buffered (concurrent) mode the shared heartbeat in
                # run_batches_concurrently reports liveness instead.
                if stream and now - last_heartbeat_time >= heartbeat_interval:
                    elapsed = now - start_time
                    quiet_for = now - last_output_time
                    print(
                        f"    Still running {batch_name} after "
                        f"{elapsed:.0f}s ({quiet_for:.0f}s since last output)...",
                        flush=True,
                    )
                    last_heartbeat_time = now
                # Process still running but no output
                time.sleep(0.1)
                continue

            chunk = os.read(process.stdout.fileno(), 4096)
            if not chunk:
                sample_rss()
                if process.poll() is not None:
                    break
                continue

            # Print output in real-time, including partial pytest progress
            # lines such as dots that do not end with newlines.
            line = chunk.decode(errors="replace")
            emit(line, end="")
            last_output_time = time.time()
            last_heartbeat_time = last_output_time
            output_lines.append(line)
            output_text += line
            if last_output_time - last_rss_sample >= 1.0:
                sample_rss()

            # Detect pytest completion
            # Look for patterns like "====== 5638 passed in 491.24s ======"
            # or "====== 2 failed, 5636 passed in 500s ======"
            if not test_completed and re.search(
                r"=+.*\d+\s+(passed|failed).*in\s+[\d.]+s.*=+",
                output_text,
            ):
                test_completed = True
                summary_at = time.time()
                # The summary line only decides how loudly a disagreement is
                # reported below; batch_status() reads the runner's status.
                failed_match = re.search(r"(\d+) failed", output_text)
                summary_reported_pass = not failed_match or (
                    int(failed_match.group(1)) == 0
                )

            # The runner has reported pytest's return value and is now only
            # tearing down, which takes tens of seconds. Stop it here, as
            # before, but keep the status it just gave us.
            marker_match = BATCH_EXIT_PATTERN.search(output_text)
            if marker_match:
                reported_returncode = int(marker_match.group(1))
                if ADMISSION is not None:
                    ADMISSION.finished()
                emit(
                    "\n    Runner reported "
                    f"{describe_exit_status(reported_returncode)}; "
                    "terminating process..."
                )
                # Final sample while the pid still exists — captures the
                # end-of-run high-water mark.
                sample_rss()
                stop_process()
                break

        # If the runner never reported, wait for the process with a timeout
        if reported_returncode is None and process.poll() is None:
            try:
                # Wait out the rest of this subprocess's budget
                elapsed = time.time() - start_time
                remaining_timeout = max(BATCH_TIMEOUT_SECONDS - elapsed, 1)
                process.wait(timeout=remaining_timeout)
            except subprocess.TimeoutExpired:
                emit(f"\n    ⏱️ Timeout - terminating process...")
                sample_rss()
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

                elapsed = time.time() - start_time
                return {
                    "elapsed": elapsed,
                    "status": "timeout",
                    "returncode": process.poll(),
                    "peak_rss_mb": peak_rss_mb,
                    "output": "".join(buf),
                }

        elapsed = time.time() - start_time

        # The runner's own report wins: the process status after a terminate is
        # the signal we sent it, not how the tests went.
        returncode = (
            reported_returncode if reported_returncode is not None else process.poll()
        )

        if abandoned == "timeout":
            emit(
                f"\n    Batch abandoned after {elapsed:.1f}s "
                f"(peak RSS: {_format_rss(peak_rss_mb)})"
            )
            return {
                "elapsed": elapsed,
                "status": "timeout",
                "returncode": returncode,
                "peak_rss_mb": peak_rss_mb,
                "output": "".join(buf),
            }

        status = batch_status(returncode)
        reported = reported_returncode is not None
        if test_completed and summary_reported_pass and status != "passed":
            # The case that used to be reported as a pass: pytest printed no
            # failure count (e.g. "1 passed, 1 error") yet finished nonzero.
            emit(
                f"    ❌ {batch_name} printed a summary with no failures but "
                f"finished with {describe_exit_status(returncode)}; "
                "the runner's status decides."
            )
        emit(
            f"\n    Batch completed in {elapsed:.1f}s "
            f"(peak RSS: {_format_rss(peak_rss_mb)}, "
            f"{describe_exit_status(returncode)})"
        )
        return {
            "elapsed": elapsed,
            "status": status,
            "returncode": returncode,
            "peak_rss_mb": peak_rss_mb,
            "output": "".join(buf),
            "reported": reported,
        }

    except Exception as e:
        elapsed = time.time() - start_time
        emit(f"\n    ❌ Error: {str(e)[:100]}")

        # Clean up process if still running
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            try:
                process.kill()
                process.wait()
            except:
                pass

        return {
            "elapsed": elapsed,
            "status": "error",
            "returncode": process.poll(),
            "peak_rss_mb": peak_rss_mb,
            "output": "".join(buf),
        }


def run_batches_concurrently(batches: List[List[str]], workers: int) -> List:
    """Run batches in a thread pool, longest-first.

    Each batch is still its own policyengine_command subprocess; the
    threads only monitor them. Output is buffered per batch and printed
    atomically (header/body/footer) when the batch finishes — only this
    (main) thread prints, so concurrent logs never interleave. A shared
    heartbeat line reports in-flight batches every ~60s.

    Returns [(batch_name, result_dict), ...] ordered by batch index.
    """
    total = len(batches)
    # Longest-first (estimated by YAML file count) so the biggest batches
    # start immediately and cannot serialize at the tail of the run.
    order = sorted(
        enumerate(batches, 1),
        key=lambda indexed: batch_cost(indexed[1]),
        reverse=True,
    )

    in_flight: Dict[str, float] = {}
    in_flight_lock = threading.Lock()

    def run_one(idx: int, batch_paths: List[str]) -> Dict:
        name = f"Batch {idx}"
        with in_flight_lock:
            in_flight[name] = time.time()
        # Output is buffered until the batch ends, so record where each batch
        # starts: a job timeout or lost runner otherwise leaves no trace of it.
        print(
            f"[Batch {idx}/{total}] started: {batch_cost(batch_paths)} files "
            f"from {batch_paths[0]}",
            flush=True,
        )
        try:
            return run_batch(batch_paths, name, stream=False)
        finally:
            if ADMISSION is not None:
                ADMISSION.forget()
            with in_flight_lock:
                in_flight.pop(name, None)

    print(
        f"\nRunning {total} batches with {workers} workers "
        f"(longest first; output buffered per batch)",
        flush=True,
    )

    results: Dict[int, Dict] = {}
    heartbeat_interval = 60
    last_heartbeat = time.time()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_info = {
            executor.submit(run_one, idx, batch_paths): (idx, batch_paths)
            for idx, batch_paths in order
        }
        pending = set(future_info)
        while pending:
            done, pending = futures_wait(
                pending, timeout=5, return_when=FIRST_COMPLETED
            )
            for future in done:
                idx, batch_paths = future_info[future]
                try:
                    result = future.result()
                except Exception as e:
                    # run_batch catches its own errors; this guards the
                    # thin wrapper so one crashed worker cannot hang the
                    # run or skip the summary.
                    result = {
                        "elapsed": 0.0,
                        "status": "error",
                        "returncode": None,
                        "peak_rss_mb": None,
                        "output": f"Worker crashed: {str(e)[:200]}\n",
                    }
                results[idx] = result
                print(f"\n[Batch {idx}/{total}] {' '.join(batch_paths)}")
                print("-" * 60)
                print(result.get("output", ""), end="")
                print(
                    f"\n[Batch {idx}/{total}] finished in "
                    f"{result['elapsed']:.1f}s | peak RSS: "
                    f"{_format_rss(result.get('peak_rss_mb'))} | "
                    f"{describe_exit_status(result.get('returncode'))} | "
                    f"{result['status']}",
                    flush=True,
                )
            now = time.time()
            if pending and now - last_heartbeat >= heartbeat_interval:
                with in_flight_lock:
                    running = ", ".join(
                        f"{name} ({now - started:.0f}s)"
                        for name, started in sorted(
                            in_flight.items(), key=lambda item: item[1]
                        )
                    )
                print(
                    f"[heartbeat] {len(pending)} batches outstanding; "
                    f"in flight: {running or 'none'}",
                    flush=True,
                )
                last_heartbeat = now

    return [(f"Batch {idx}", results[idx]) for idx in sorted(results)]


def main():
    """Main entry point for the generic test runner."""

    parser = argparse.ArgumentParser(
        description="Run tests in batches with memory cleanup between batches"
    )
    parser.add_argument("test_path", help="Path to the test directory")
    parser.add_argument(
        "--batches",
        type=int,
        default=2,
        help="Number of batches to split tests into (default: 2)",
    )
    parser.add_argument(
        "--exclude",
        type=str,
        default="",
        help="Comma-separated list of directory names to exclude (for contrib tests)",
    )
    parser.add_argument(
        "--shard",
        type=str,
        default=None,
        help="Run a shard of the batches across parallel CI runners (format: 'I/N'; 1-indexed)",
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "per-subdir", "per-file"],
        default="auto",
        help="Batching mode. 'per-subdir' = each immediate subdir is its own batch, split by reform-combo weight when over budget; 'per-file' = each yaml is its own batch.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of batches to run concurrently (default: 1 = sequential)",
    )

    args = parser.parse_args()
    scheduled = bool(os.environ.get(WORKERS_ENV))
    if scheduled:
        args.workers = int(os.environ[WORKERS_ENV])
    exclude_list = [x.strip() for x in args.exclude.split(",") if x.strip()]

    shard_idx = shard_count = None
    if args.shard:
        try:
            shard_idx, shard_count = (int(x) for x in args.shard.split("/"))
        except ValueError:
            print(f"Error: --shard must be in format 'I/N' (got {args.shard!r})")
            sys.exit(1)
        if not (1 <= shard_idx <= shard_count):
            print(f"Error: --shard I must satisfy 1 <= I <= N (got {args.shard!r})")
            sys.exit(1)

    if args.workers < 1:
        print(f"Error: --workers must be >= 1 (got {args.workers})")
        sys.exit(1)

    if not os.path.exists("policyengine_us"):
        print("Error: Must run from PolicyEngine US root directory")
        sys.exit(1)

    test_path = Path(args.test_path)
    if not test_path.exists():
        print(f"Error: Test path does not exist: {args.test_path}")
        sys.exit(1)

    print(f"PolicyEngine Test Runner")
    print("=" * 60)
    print(f"Test path: {test_path}")
    print(f"Requested batches: {args.batches}")
    if args.workers > 1:
        print(f"Workers: {args.workers}")
    if exclude_list:
        print(f"Excluding: {', '.join(exclude_list)}")

    # Count total tests
    total_tests = count_yaml_files(test_path)
    print(f"Total test files: {total_tests}")

    # Split into batches
    batches = split_into_batches(test_path, args.batches, exclude_list, args.mode)

    # Apply sharding: slice every Nth batch starting from the shard index.
    # Alphabetical subfolder ordering means new folders auto-distribute by
    # position rather than requiring manual re-assignment per runner.
    # (An earlier special case pinned RI's batches to the last shard because
    # RI was far heavier than any other state; combo-weight packing now caps
    # every batch at the same budget, so the plain stride applies.)
    if shard_count is not None:
        all_batch_count = len(batches)
        batches = batches[shard_idx - 1 :: shard_count]
        print(
            f"Sharding: running shard {shard_idx}/{shard_count} "
            f"({len(batches)} of {all_batch_count} batches)"
        )

    global ADMISSION
    if scheduled and args.workers > 1:
        if len(batches) < args.workers:
            batches = fill_workers(batches, args.workers)
            print(f"Split into {len(batches)} batches for {args.workers} workers")
        ADMISSION = Admission()

    if len(batches) != args.batches:
        print(f"Actual batches: {len(batches)} (optimized for {total_tests} files)")
    else:
        print(f"Actual batches: {len(batches)}")
    print("=" * 60)

    # Run batches
    run_start = time.time()
    if args.workers > 1:
        results = run_batches_concurrently(batches, args.workers)
    else:
        results = []
        for i, batch_paths in enumerate(batches, 1):
            print(f"\n[Batch {i}/{len(batches)}]")

            # Show what's in this batch
            print(f"  Test files: ~{batch_cost(batch_paths)}")
            print("-" * 60)

            result = run_batch(batch_paths, f"Batch {i}")
            results.append((f"Batch {i}", result))

            # Memory cleanup after each batch
            print("  Cleaning up memory...")
            gc.collect()

    any_failed = any(result["status"] != "passed" for _, result in results)
    total_elapsed = sum(result["elapsed"] for _, result in results)

    # Final summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total test files: {total_tests}")
    for name, result in results:
        print(
            f"  {name}: {result['elapsed']:.1f}s | "
            f"peak RSS: {_format_rss(result.get('peak_rss_mb'))} | "
            f"{describe_exit_status(result.get('returncode'))} | "
            f"{result['status']}"
        )
    print(f"Workers: {args.workers}")
    if ADMISSION is not None:
        ADMISSION.stopped = True
        print(
            f"[memory] admission waits: {ADMISSION.waits}, "
            f"evictions: {ADMISSION.evictions}"
        )
    print(f"Total time: {total_elapsed:.1f}s")
    if args.workers > 1:
        print(f"Wall time: {time.time() - run_start:.1f}s")

    # Exit code
    sys.exit(1 if any_failed else 0)


if __name__ == "__main__":
    main()
