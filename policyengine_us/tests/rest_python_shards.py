#!/usr/bin/env python
"""Plan the Rest Python tests over parallel CI shards, and run one shard.

`make test-other-python-rest` runs one pytest process per group in
REST_PYTHON_GROUPS (Makefile): modules that retain full systems sit in their
own groups, so no process outgrows the 16 GB runner. CI used to run those
groups on two runners, the second waiting for the first. By October 2026 one
file, test_behavioral_response_measurement_copies.py (27 minutes), had taken
the core group to 50 minutes and the two runners to 130 (CI run 40014592006),
the longest path of every PR.

`plan` reads the groups from the Makefile and pytest's own collection, and
each file's time from the JUnit reports of a recent CI run. A group longer
than the target splits into chunks of about the target, longest files first,
each chunk keeping the group's file order. Chunks and whole groups then go to
the least-loaded shard, longest first, over as few shards as keep the longest
near the target or the longest single chunk. A process still runs files of
one group only, so none holds more than its group did. A file without a
recorded time counts as its group's median. Without any reports every file
counts the same, and the plan still runs each file once, only less evenly.

`run` runs one shard's processes in turn, each with its own JUnit and GNU
time report when given a report directory, and fails if any of them fails.
code_health/test_rest_python_groups.py checks that every plan runs each file
of the groups exactly once.
"""

import argparse
import json
import math
import os
import re
import shlex
import statistics
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree

REPO = Path(__file__).resolve().parents[2]

# Each shard aims at about this many minutes. The Baseline and Contrib chain
# takes about 70, so the Python shards finish well inside it.
TARGET_MINUTES = 25
# Bounds on the shard count whatever the reports say: missing or tiny times
# cannot pile every group onto one runner.
MIN_SHARDS = 4
MAX_SHARDS = 12
# A plan whose longest shard is within this of the bound is good enough;
# another runner would only shave a minute or two.
MAKESPAN_TOLERANCE = 1.05
# Interpreter start, model import and collection, per process, when no
# report measures it (CI run 40014592006: 50-105 s per group).
DEFAULT_PROCESS_SECONDS = 60
# Per file when no report covers any file of the group: the Rest groups
# averaged 27 s per file in CI run 40014592006.
DEFAULT_FILE_SECONDS = 30
DEFAULT_VARIABLES_SECONDS = 90

# A make run passes these on to the make the planner starts, where they
# would add or remove report options from the groups' commands.
PARENT_MAKE_VARIABLES = ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "REST_REPORT_DIR")
REPORT_MARKER = "@rest-report-dir@"


def make_groups(cwd=REPO):
    """Each Rest group's pytest arguments, in run order, from make's dry run.

    The group name comes from its JUnit file, rest-python-<group>.xml.
    """
    env = {k: v for k, v in os.environ.items() if k not in PARENT_MAKE_VARIABLES}
    result = subprocess.run(
        [
            "make",
            "-n",
            "--no-print-directory",
            "test-other-python-rest",
            f"REST_REPORT_DIR={REPORT_MARKER}",
        ],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    groups = {}
    junit = re.compile(rf"--junitxml={re.escape(REPORT_MARKER)}/rest-python-(.+)\.xml")
    for line in result.stdout.splitlines():
        if not line.startswith("/usr/bin/time "):
            continue
        argv = shlex.split(line)
        if argv[:3] != ["/usr/bin/time", "-v", "-o"] or argv[4] != "pytest":
            raise RuntimeError(f"unexpected group command: {line}")
        names = [m.group(1) for arg in argv[5:] if (m := junit.fullmatch(arg))]
        if len(names) != 1 or names[0] in groups:
            raise RuntimeError(f"cannot name the group of: {line}")
        args = [arg for arg in argv[5:] if not junit.fullmatch(arg)]
        # A shard passes pytest only the collected files and --maxfail=0, so
        # any other option (-p, -m, --deselect...) would be lost in CI.
        unsupported = [
            arg
            for arg in args
            if arg.startswith("-")
            and arg != "--maxfail=0"
            and not arg.startswith("--ignore=")
        ]
        if unsupported:
            raise RuntimeError(f"shards cannot pass on {unsupported}: {line}")
        groups[names[0]] = args
    if not groups:
        raise RuntimeError("make test-other-python-rest runs no groups")
    return groups


def collected_files(args, cwd=REPO):
    """The test files pytest collects for these arguments, relative to cwd.

    Nothing is imported: the `list-files` mode below swaps each test module
    for a placeholder and skips conftest.py files. A command that collects
    nothing (pytest's exit 5) lists no files.
    """
    env = {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}
    with tempfile.TemporaryDirectory() as tmp:
        listing = Path(tmp) / "files.json"
        result = subprocess.run(
            [sys.executable, __file__, "list-files", str(listing), *args],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
        )
        if result.returncode not in (0, 5):
            raise RuntimeError(f"{args}:\n{result.stdout}{result.stderr}")
        return json.loads(listing.read_text())


def group_files(cwd=REPO):
    """Each group's test files, in the order its pytest process runs them."""
    return {
        group: collected_files(args, cwd) for group, args in make_groups(cwd).items()
    }


# --- Times from CI reports -----------------------------------------------------


def file_of(classname, files):
    """The test file of a JUnit classname, which is its node ID's path with
    dots for slashes, followed by any class names."""
    parts = classname.split(".")
    for end in range(len(parts), 0, -1):
        candidate = "/".join(parts[:end]) + ".py"
        if candidate in files:
            return candidate
    return None


def wall_seconds(resources):
    """The elapsed time in a GNU time -v report, or None without one."""
    if not resources.exists():
        return None
    for line in resources.read_text().splitlines():
        if "Elapsed (wall clock) time" in line:
            fields = [float(x) for x in line.rsplit(" ", 1)[1].split(":")]
            return sum(x * 60**i for i, x in enumerate(reversed(fields)))
    return None


def read_timings(directory, files):
    """Seconds per test file, per process outside its tests, and for the
    variables YAML, from the reports under a directory.

    Files no report covers are absent; the other two are None when no report
    measures them. A re-run release run also keeps its earlier attempts'
    reports under names the later plan did not reuse, so a file two reports
    cover counts once, at the longer time.
    """
    known = set(files)
    seconds = {}
    overheads = []
    variables = None
    if directory is not None and Path(directory).is_dir():
        for xml in sorted(Path(directory).rglob("rest-python-*.xml")):
            try:
                root = ElementTree.parse(xml).getroot()
            except ElementTree.ParseError:
                continue
            total = 0.0
            report = defaultdict(float)
            for case in root.iter("testcase"):
                time = float(case.get("time") or 0)
                total = total + time
                file = file_of(case.get("classname", ""), known)
                if file is not None:
                    report[file] = report[file] + time
            for file, time in report.items():
                seconds[file] = max(time, seconds.get(file, 0.0))
            wall = wall_seconds(xml.with_name(f"{xml.stem}-resources.txt"))
            if wall is not None:
                overheads.append(max(0.0, wall - total))
        for resources in Path(directory).rglob("rest-variables-resources.txt"):
            variables = wall_seconds(resources)
    overhead = statistics.median(overheads) if overheads else None
    return seconds, overhead, variables


# --- Planning ------------------------------------------------------------------


def estimates(groups, seconds):
    """Seconds per file: its recorded time, else its group's median, else the
    median over all groups, else DEFAULT_FILE_SECONDS."""
    recorded = [seconds[f] for files in groups.values() for f in files if f in seconds]
    fallback = statistics.median(recorded) if recorded else DEFAULT_FILE_SECONDS
    result = {}
    for files in groups.values():
        known = [seconds[f] for f in files if f in seconds]
        group_fallback = statistics.median(known) if known else fallback
        for file in files:
            result[file] = seconds.get(file, group_fallback)
    return result


def longest_first(items, bins, weight):
    """Deal items, longest first, each to the least-loaded of `bins` bins.

    Ties go to the lowest bin, so the result depends only on the inputs.
    """
    loads = [0.0] * bins
    contents = [[] for _ in range(bins)]
    for item in sorted(items, key=lambda item: -weight(item)):
        target = min(range(bins), key=lambda i: (loads[i], i))
        loads[target] = loads[target] + weight(item)
        contents[target].append(item)
    return contents, loads


def chunk_group(group, files, cost, target_seconds):
    """Split a group longer than the target into chunks of about the target.

    Each chunk keeps the group's file order, so a chunk's process meets its
    files in the order the whole group's process did.
    """
    total = sum(cost[f] for f in files)
    count = max(1, min(len(files), math.ceil(total / target_seconds)))
    if count == 1:
        return [(group, list(files))]
    order = {f: i for i, f in enumerate(files)}
    contents, _ = longest_first(files, count, cost.__getitem__)
    chunks = [sorted(chunk, key=order.__getitem__) for chunk in contents if chunk]
    chunks.sort(key=lambda chunk: order[chunk[0]])
    return [(f"{group}-{i}", chunk) for i, chunk in enumerate(chunks, start=1)]


def make_plan(
    groups,
    seconds=None,
    overhead=None,
    variables=None,
    target_minutes=TARGET_MINUTES,
    min_shards=MIN_SHARDS,
    max_shards=MAX_SHARDS,
):
    """Shards of processes that run every group's files once.

    Each process runs files of one group, in that group's order. The shard
    count is the smallest in [min_shards, max_shards] whose longest shard is
    within MAKESPAN_TOLERANCE of the target, or of the longest process when
    that is longer. The variables YAML runs on the least-loaded shard.
    """
    seconds = seconds or {}
    overhead = DEFAULT_PROCESS_SECONDS if overhead is None else overhead
    variables = DEFAULT_VARIABLES_SECONDS if variables is None else variables
    target = target_minutes * 60
    cost = estimates(groups, seconds)
    processes = []
    for group, files in groups.items():
        for name, chunk in chunk_group(group, files, cost, target):
            estimate = overhead + sum(cost[f] for f in chunk)
            processes.append(
                {"name": name, "group": group, "files": chunk, "seconds": estimate}
            )
    if not processes:
        raise ValueError("no test files to plan")
    weight = lambda process: process["seconds"]  # noqa: E731
    bound = MAKESPAN_TOLERANCE * max(target, max(map(weight, processes)))
    upper = max(1, min(max_shards, len(processes)))
    count = min(min_shards, upper)
    while True:
        contents, loads = longest_first(processes, count, weight)
        if max(loads) <= bound or count == upper:
            break
        count = count + 1
    lightest = min(range(count), key=lambda i: (loads[i], i))
    loads[lightest] = loads[lightest] + variables
    order = {p["name"]: i for i, p in enumerate(processes)}
    shards = [
        {
            "shard": i + 1,
            "minutes": round(loads[i] / 60, 1),
            "variables": i == lightest,
            "processes": [
                {"name": p["name"], "group": p["group"], "files": p["files"]}
                for p in sorted(contents[i], key=lambda p: order[p["name"]])
            ],
        }
        for i in range(count)
    ]
    check_plan(groups, shards)
    return shards


def check_plan(groups, shards):
    """Raise unless the shards run each group's files once, in group order,
    with no process mixing groups and no shard idle."""
    seen = defaultdict(list)
    names = set()
    for shard in shards:
        if not shard["processes"]:
            raise AssertionError(f"shard {shard['shard']} runs nothing")
        for process in shard["processes"]:
            if process["name"] in names:
                raise AssertionError(f"process {process['name']} runs twice")
            names.add(process["name"])
            group = groups.get(process["group"])
            if group is None or not process["files"]:
                raise AssertionError(f"process {process['name']} has no group files")
            order = [group.index(f) if f in group else -1 for f in process["files"]]
            if -1 in order or order != sorted(order):
                raise AssertionError(
                    f"process {process['name']} runs files outside its group's order"
                )
            for file in process["files"]:
                seen[file].append(process["name"])
    expected = [f for files in groups.values() for f in files]
    missing = sorted(set(expected) - set(seen))
    repeated = sorted(f for f, owners in seen.items() if len(owners) > 1)
    if missing or repeated or len(expected) != len(set(expected)):
        raise AssertionError(f"missing: {missing}; repeated: {repeated}")
    if sum(shard["variables"] for shard in shards) != 1:
        raise AssertionError("the variables YAML must run on exactly one shard")


def matrix(shards):
    """The GitHub Actions matrix: each shard's processes as a JSON string."""
    return {
        "include": [
            {
                "shard": shard["shard"],
                "variables": shard["variables"],
                "processes": json.dumps(shard["processes"], separators=(",", ":")),
            }
            for shard in shards
        ]
    }


def summary(shards, source):
    lines = [
        f"Rest Python plan: {len(shards)} shards, times from {source}.",
        "",
        "| Shard | Estimated minutes | Processes (files) |",
        "|---:|---:|---|",
    ]
    for shard in shards:
        processes = ", ".join(
            f"{p['name']} ({len(p['files'])})" for p in shard["processes"]
        )
        if shard["variables"]:
            processes = processes + ", variables YAML"
        lines.append(f"| {shard['shard']} | {shard['minutes']} | {processes} |")
    return "\n".join(lines) + "\n"


# --- Running a shard -----------------------------------------------------------


def run_processes(processes, report_dir=None):
    """Run each process in turn; 1 if any failed, was killed or is missing."""
    if not processes:
        print("This shard has no Rest Python processes to run.")
        return 1
    failed = []
    for process in processes:
        name = process["name"]
        print(f"=== Rest Python group: {name} ({len(process['files'])} files) ===")
        sys.stdout.flush()
        command = ["pytest", *process["files"], "--maxfail=0"]
        if report_dir is not None:
            command = [
                "/usr/bin/time",
                "-v",
                "-o",
                f"{report_dir}/rest-python-{name}-resources.txt",
                *command,
                f"--junitxml={report_dir}/rest-python-{name}.xml",
            ]
        if subprocess.run(command).returncode != 0:
            failed.append(name)
    if failed:
        print(f"Failed Rest Python groups: {' '.join(failed)}")
        return 1
    return 0


# --- Listing collected files without importing them ----------------------------


def list_files(output, pytest_args):
    import pytest

    class Unimported(pytest.File):
        """A test file pytest would import, standing in as one item."""

        def collect(self):
            yield Placeholder.from_parent(self, name=self.path.name)

    class Placeholder(pytest.Item):
        def runtest(self):
            raise AssertionError("listed for collection only")

    class FileListing:
        def __init__(self):
            self.files = []

        @pytest.hookimpl(tryfirst=True)
        def pytest_pycollect_makemodule(self, module_path, parent):
            return Unimported.from_parent(parent, path=module_path)

        def pytest_collection_finish(self, session):
            # Read the kept items, not the modules built: for a file argument
            # pytest builds a module for each file beside it, then keeps one.
            self.files = [
                Path(os.path.relpath(item.path)).as_posix() for item in session.items
            ]

    listing = FileListing()
    status = pytest.main(
        [
            *pytest_args,
            "--collect-only",
            "-q",
            "--noconftest",
            "-p",
            "no:cacheprovider",
        ],
        plugins=[listing],
    )
    Path(output).write_text(json.dumps(listing.files))
    return int(status)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["list-files"]:
        return list_files(argv[1], argv[2:])
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="plan the shards")
    plan.add_argument("--timings", help="directory of CI timing reports")
    plan.add_argument("--source", default="no reports", help="where they came from")
    plan.add_argument("--github-output", help="file to append matrix=<json> to")
    plan.add_argument("--summary", help="file to append a Markdown summary to")
    plan.add_argument("--target-minutes", type=float, default=TARGET_MINUTES)
    run = commands.add_parser("run", help="run one shard's processes")
    run.add_argument(
        "--processes-env",
        default="REST_PYTHON_PROCESSES",
        help="environment variable holding the shard's processes as JSON",
    )
    run.add_argument("--report-dir", help="write JUnit and GNU time reports here")
    args = parser.parse_args(argv)

    if args.command == "run":
        processes = json.loads(os.environ.get(args.processes_env) or "[]")
        return run_processes(processes, args.report_dir)

    groups = group_files()
    files = [f for group in groups.values() for f in group]
    seconds, overhead, variables = read_timings(args.timings, files)
    source = args.source
    if not seconds:
        print("::warning::No Rest Python timing reports; every file counts the same.")
        source = "no reports (every file counts the same)"
    else:
        covered = sum(f in seconds for f in files)
        source = f"{source} ({covered} of {len(files)} files timed)"
    shards = make_plan(groups, seconds, overhead, variables, args.target_minutes)
    text = summary(shards, source)
    print(text)
    print(json.dumps(shards, indent=1))
    if args.github_output:
        with open(args.github_output, "a") as output:
            output.write(f"matrix={json.dumps(matrix(shards))}\n")
    if args.summary:
        with open(args.summary, "a") as output:
            output.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
