"""Each remaining Python test file runs in exactly one Rest group and shard.

The Rest CI job used to run every Python test outside contrib, microsimulation
and the SPM files in one pytest process. That process peaked at 15.7 GB RSS on
the 16 GB runner (CI run 37198184683), and later runs lost the runner partway
through the step. `make test-other-python-rest` now runs the same files as one
pytest process per group in REST_PYTHON_GROUPS. In CI, rest_python_shards.py
plans those groups' files over parallel shards from a recent run's times,
splitting a long group into chunks. A process runs files of one group only,
and Rest keeps the original check, failing unless every shard succeeded.

Paths and --ignore flags can drop a file, or run it twice, while every test
still passes. So this guard expands the groups through `make -n`, asks pytest
which files each group collects, and checks that each file of the old single
command runs exactly once. A new test file lands in core or policy when it
sits under those folders and in remaining otherwise; the check fails if a
change to the groups leaves one out. Plans made with no, measured, skewed and
tiny times must then run each group's files once, in the group's order, and
the workflows must run and upload each shard of the plan. Running the target
and a shard with a stub pytest checks that every process runs and that any
failure fails them. The original Rest check aggregates the plan and shards,
and must fail on failed, cancelled or skipped jobs.

pytest lists the files here through its own discovery (paths, --ignore,
python_files), but nothing is imported: rest_python_shards.py's list-files
mode swaps each test module for a placeholder. It also skips conftest.py
files, because importing policyengine_us/conftest.py imports the whole model.
test_conftest_files_cannot_change_which_files_are_collected keeps that safe.
"""

import ast
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import zlib
from collections import defaultdict
from fnmatch import fnmatch
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
TESTS = REPO / "policyengine_us" / "tests"
PLANNER = TESTS / "rest_python_shards.py"
SPEC = importlib.util.spec_from_file_location("rest_python_shards", PLANNER)
shards = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(shards)
WORKFLOWS = [
    REPO / ".github" / "workflows" / name for name in ("python-tests.yaml", "push.yaml")
]
KEEP_RUNNING_WITH_SYSTEM_CA = (
    "${{ !cancelled() && steps.system-ca.outcome == 'success' }}"
)
RELEASE_ONLY = (
    "(github.repository == 'PolicyEngine/policyengine-us') "
    "&& (github.event.head_commit.message == 'Update PolicyEngine US')"
)
# CI runs this file in a Rest shard, and a local `make test` exports these.
# Passed on, they would add report options to the guard's reference commands,
# or carry a report directory into the stub run and overwrite real reports.
PARENT_MAKE_VARIABLES = ("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "REST_REPORT_DIR")
REPORT_DIR = "reports"
PLANNER_COMMAND = "python policyengine_us/tests/rest_python_shards.py"


def dry_run(target, *overrides, prefixes=("pytest ", "/usr/bin/time ")):
    """The commands `make <target>` runs, each split into its arguments."""
    if shutil.which("make") is None:
        pytest.skip("make is not installed")
    env = {k: v for k, v in os.environ.items() if k not in PARENT_MAKE_VARIABLES}
    result = subprocess.run(
        ["make", "-n", "--no-print-directory", target, *overrides],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return [
        shlex.split(line)
        for line in result.stdout.splitlines()
        if line.startswith(prefixes)
    ]


def collected_files(args, cwd=REPO):
    """The test files pytest collects for these arguments, relative to cwd.

    A command that collects nothing (pytest's exit 5) lists no files, which
    partition_problems reports by group.
    """
    return shards.collected_files(args, cwd)


def partition_problems(reference, groups):
    """How the groups' files fail to cover each reference file exactly once."""
    owners = defaultdict(list)
    for group, files in groups.items():
        for file in files:
            owners[file].append(group)
    problems = [
        f"{group} collects no files" for group, files in groups.items() if not files
    ]
    problems += [
        f"{file} is collected by no group"
        for file in sorted(set(reference) - set(owners))
    ]
    for file, file_groups in sorted(owners.items()):
        if len(file_groups) > 1:
            problems.append(f"{file} is collected by {', '.join(file_groups)}")
        if file not in reference:
            problems.append(
                f"{file} is collected by {', '.join(file_groups)} but was not "
                "in the old single process"
            )
    return problems


def workflow_jobs(workflow):
    return yaml.safe_load(workflow.read_text())["jobs"]


def single(steps, predicate):
    (step,) = [step for step in steps if predicate(step)]
    return step


def assert_system_ca_precedes(steps, runtime_step):
    """Continuations require a successful, unconditional CA setup first."""
    setup = single(
        steps, lambda step: step.get("uses") == "./.github/actions/setup-system-ca"
    )
    assert setup["id"] == "system-ca"
    assert "if" not in setup
    assert not setup.get("continue-on-error", False)
    assert steps.index(setup) == 1
    assert steps[0]["uses"].startswith("actions/checkout@")
    assert steps.index(setup) < steps.index(runtime_step)


def reported_groups(report_dir, *overrides):
    """Each group's pytest arguments and report files, in run order.

    The group name comes from the JUnit file, rest-python-<group>.xml.
    """
    groups = {}
    for argv in dry_run(
        "test-other-python-rest", f"REST_REPORT_DIR={report_dir}", *overrides
    ):
        assert argv[:3] == ["/usr/bin/time", "-v", "-o"], argv
        assert argv[4] == "pytest", argv
        junit = [arg for arg in argv[5:] if arg.startswith("--junitxml=")]
        assert len(junit) == 1, argv
        xml = junit[0].removeprefix("--junitxml=")
        match = re.fullmatch(rf"{re.escape(report_dir)}/rest-python-(.+)\.xml", xml)
        assert match, xml
        group = match.group(1)
        assert group not in groups, f"{group} runs twice"
        assert argv[3] == f"{report_dir}/rest-python-{group}-resources.txt", argv
        groups[group] = {
            "args": [arg for arg in argv[5:] if arg != junit[0]],
            "reports": [xml, argv[3]],
        }
    return groups


@pytest.fixture(scope="module")
def groups():
    return reported_groups(REPORT_DIR)


@pytest.fixture(scope="module")
def old_command():
    """The pytest arguments of the single process the groups replace.

    It was test-other-python, the Python tests outside contrib and
    microsimulation, with the SPM files left to their own step.
    """
    (other,) = dry_run("test-other-python")
    (spm,) = dry_run("test-other-python-spm")
    assert other[0] == spm[0] == "pytest", (other, spm)
    spm_files = [arg for arg in spm[1:] if not arg.startswith("-")]
    return other[1:] + [f"--ignore={file}" for file in spm_files]


@pytest.fixture(scope="module")
def reference(old_command):
    return collected_files(old_command)


@pytest.fixture(scope="module")
def group_files(groups):
    return {group: collected_files(spec["args"]) for group, spec in groups.items()}


def test_groups_collect_each_file_of_the_old_single_process_once(
    group_files, reference
):
    # The reference is a real collection: it holds this file.
    assert Path(__file__).relative_to(REPO).as_posix() in reference
    problems = partition_problems(reference, group_files)
    assert not problems, "\n".join(problems)


def test_planner_reads_the_groups_the_makefile_runs(groups):
    assert shards.make_groups() == {
        group: spec["args"] for group, spec in groups.items()
    }


def stable_seconds(file, low, high):
    """A per-file time in [low, high) that depends only on the file name."""
    return low + (zlib.crc32(file.encode()) % 1000) / 1000 * (high - low)


def timing_scenarios(group_files):
    files = [f for group in group_files.values() for f in group]
    copies = "policyengine_us/tests/core/test_behavioral_response_measurement_copies.py"
    measured = {f: stable_seconds(f, 0.5, 60) for f in files}
    skewed = dict(measured)
    skewed[files[0]] = 40 * 60
    if copies in skewed:
        skewed[copies] = 27 * 60
    return {
        "no reports": {},
        "measured": measured,
        "partly measured": {
            f: s for f, s in measured.items() if zlib.crc32(f.encode()) % 3
        },
        "one file past the target": skewed,
        "tiny": {f: 0.1 for f in files},
        "huge": {f: 600 for f in files},
    }


@pytest.mark.parametrize(
    "scenario",
    [
        "no reports",
        "measured",
        "partly measured",
        "one file past the target",
        "tiny",
        "huge",
    ],
)
def test_every_plan_runs_each_group_file_once_in_group_order(
    group_files, reference, scenario
):
    seconds = timing_scenarios(group_files)[scenario]
    plan = shards.make_plan(group_files, seconds)
    assert shards.MIN_SHARDS <= len(plan) <= shards.MAX_SHARDS
    assert [shard["shard"] for shard in plan] == list(range(1, len(plan) + 1))
    assert sum(shard["variables"] for shard in plan) == 1
    selected = {}
    names = []
    for shard in plan:
        assert shard["processes"], f"shard {shard['shard']} runs nothing"
        for process in shard["processes"]:
            names.append(process["name"])
            group = group_files[process["group"]]
            assert process["name"] == process["group"] or re.fullmatch(
                rf"{re.escape(process['group'])}-\d+", process["name"]
            )
            # One group per process, in the order its group's process ran.
            positions = [group.index(file) for file in process["files"]]
            assert positions == sorted(positions), process["name"]
            selected[f"shard {shard['shard']}/{process['name']}"] = process["files"]
    # Process names become report names, which must not collide.
    assert len(names) == len(set(names)), names
    problems = partition_problems(reference, selected)
    assert not problems, f"{scenario}:\n" + "\n".join(problems)


def test_a_long_group_splits_and_its_longest_file_runs_alone():
    groups = {
        "core": [f"core/test_{i:03d}.py" for i in range(115)],
        "remaining": [f"test_{i:03d}.py" for i in range(87)],
        "heavy": ["test_heavy.py"],
    }
    seconds = {f: 12 for f in groups["core"]} | {f: 15 for f in groups["remaining"]}
    seconds["core/test_050.py"] = 27 * 60
    seconds["test_heavy.py"] = 6 * 60
    plan = shards.make_plan(groups, seconds, overhead=60, variables=70)
    processes = {p["name"]: p for shard in plan for p in shard["processes"]}
    # 50 core minutes split at 25; the 27-minute file fills a chunk alone.
    assert sorted(processes) == ["core-1", "core-2", "heavy", "remaining"]
    assert ["core/test_050.py"] in [p["files"] for p in processes.values()]
    # Groups shorter than the target keep one process.
    assert processes["remaining"]["files"] == groups["remaining"]


def rest_shaped_groups():
    """Groups and times shaped like the October 2026 Rest reports."""
    sizes = {
        "cached-arrays": (1, 390),
        "heavy-a": (4, 85),
        "heavy-b": (4, 150),
        "core-heavy": (3, 140),
        "core": (115, 12),
        "policy-parameters": (3, 70),
        "policy": (25, 33),
        "remaining-heavy": (6, 80),
        "remaining": (87, 15),
    }
    groups = {
        group: [f"{group}/test_{i:03d}.py" for i in range(count)]
        for group, (count, _) in sizes.items()
    }
    seconds = {
        file: sizes[group][1] for group, files in groups.items() for file in files
    }
    seconds["core/test_050.py"] = 27 * 60
    return groups, seconds


def test_the_plan_uses_the_fewest_shards_that_keep_the_longest_near_the_bound():
    groups, seconds = rest_shaped_groups()
    plan = shards.make_plan(groups, seconds, overhead=60, variables=70)
    cost = shards.estimates(groups, seconds)
    weights = {
        p["name"]: 60 + sum(cost[f] for f in p["files"])
        for shard in plan
        for p in shard["processes"]
    }
    bound = shards.MAKESPAN_TOLERANCE * max(
        shards.TARGET_MINUTES * 60, max(weights.values())
    )
    loads = [sum(weights[p["name"]] for p in shard["processes"]) for shard in plan]
    assert max(loads) <= bound
    # One shard fewer cannot meet the bound, so the plan uses no extra runner.
    _, fewer = shards.longest_first(list(weights), len(plan) - 1, weights.get)
    assert max(fewer) > bound
    assert len(plan) == 6
    # The variables YAML goes to the least-loaded shard.
    (marked,) = [i for i, shard in enumerate(plan) if shard["variables"]]
    assert loads[marked] == min(loads)
    assert plan[marked]["minutes"] == round((loads[marked] + 70) / 60, 1)


def test_plans_without_times_count_files_evenly_and_stay_complete():
    groups = {"a": [f"a/test_{i:03d}.py" for i in range(300)], "b": ["b/test_0.py"]}
    plan = shards.make_plan(groups)
    processes = [p for shard in plan for p in shard["processes"]]
    files = sorted(f for p in processes for f in p["files"])
    assert files == sorted(groups["a"] + groups["b"])
    # 300 files at DEFAULT_FILE_SECONDS make 150 minutes: six equal chunks,
    # 26 minutes each with process start. b cannot join one of them within
    # the tolerance, so it gets a seventh shard, which also runs variables.
    chunks = [len(p["files"]) for p in processes if p["group"] == "a"]
    assert chunks == [50] * 6
    assert len(plan) == 7
    assert max(shard["minutes"] for shard in plan) == 26.0
    (marked,) = [shard for shard in plan if shard["variables"]]
    assert [p["group"] for p in marked["processes"]] == ["b"]


def test_the_planner_refuses_group_options_a_shard_cannot_pass_on(tmp_path):
    command = (
        "\t/usr/bin/time -v -o $(REST_REPORT_DIR)/rest-python-a-resources.txt "
        "pytest a --maxfail=0 --ignore=a/b{extra} "
        "--junitxml=$(REST_REPORT_DIR)/rest-python-a.xml\n"
    )
    makefile = tmp_path / "Makefile"
    makefile.write_text("test-other-python-rest:\n" + command.format(extra=""))
    assert shards.make_groups(tmp_path) == {"a": ["a", "--maxfail=0", "--ignore=a/b"]}
    makefile.write_text(
        "test-other-python-rest:\n" + command.format(extra=" -p no:randomly")
    )
    with pytest.raises(RuntimeError, match=r"cannot pass on \['-p'\]"):
        shards.make_groups(tmp_path)


def test_the_plan_command_writes_a_complete_matrix_and_summary(tmp_path, group_files):
    files = [f for group in group_files.values() for f in group]
    write_report(
        tmp_path / "timings" / "rest-python-test-timings-shard-1",
        "rest-python-core",
        [(file.removesuffix(".py").replace("/", "."), 30) for file in files[:20]],
        wall="12:00",
    )
    output = tmp_path / "github-output"
    summary = tmp_path / "summary.md"
    result = subprocess.run(
        [
            sys.executable,
            str(PLANNER),
            "plan",
            "--timings",
            str(tmp_path / "timings"),
            "--source",
            "release run 1",
            "--github-output",
            str(output),
            "--summary",
            str(summary),
        ],
        cwd=REPO,
        env={k: v for k, v in os.environ.items() if k not in PARENT_MAKE_VARIABLES},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    (line,) = output.read_text().splitlines()
    assert line.startswith("matrix=")
    entries = json.loads(line.removeprefix("matrix="))["include"]
    planned = [
        file
        for entry in entries
        for process in json.loads(entry["processes"])
        for file in process["files"]
    ]
    assert sorted(planned) == sorted(files)
    assert sum(entry["variables"] for entry in entries) == 1
    assert summary.read_text().startswith(
        f"Rest Python plan: {len(entries)} shards, times from release run 1 "
        f"(20 of {len(files)} files timed)."
    )


def test_unknown_files_count_as_their_groups_median():
    groups = {"a": ["a1.py", "a2.py", "a3.py", "new.py"], "b": ["b1.py", "b2.py"]}
    seconds = {"a1.py": 10, "a2.py": 20, "a3.py": 300, "b1.py": 1, "b2.py": 3}
    assert shards.estimates(groups, seconds)["new.py"] == 20
    assert shards.estimates({"c": ["c1.py"]} | groups, seconds)["c1.py"] == 10


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda plan: plan[0]["processes"][0]["files"].pop(), "missing"),
        (
            lambda plan: plan[1]["processes"][0]["files"].append("a/test_0.py"),
            "outside its group",
        ),
        (
            lambda plan: plan[0]["processes"][0]["files"].reverse(),
            "outside its group",
        ),
        (
            lambda plan: plan[1]["processes"].append(
                dict(plan[0]["processes"][0], name="a-2")
            ),
            "repeated",
        ),
        (lambda plan: plan[1]["processes"].clear(), "runs nothing"),
        (lambda plan: plan[1].update(variables=True), "exactly one shard"),
        (
            lambda plan: plan[1]["processes"][0].update(name="a"),
            "runs twice",
        ),
    ],
)
def test_the_plan_check_rejects_dropped_repeated_or_mixed_files(change, message):
    groups = {"a": ["a/test_0.py", "a/test_1.py"], "b": ["b/test_0.py"]}
    plan = [
        {
            "shard": 1,
            "variables": True,
            "processes": [{"name": "a", "group": "a", "files": list(groups["a"])}],
        },
        {
            "shard": 2,
            "variables": False,
            "processes": [{"name": "b", "group": "b", "files": list(groups["b"])}],
        },
    ]
    shards.check_plan(groups, plan)
    change(plan)
    with pytest.raises(AssertionError, match=message):
        shards.check_plan(groups, plan)


def write_report(directory, name, cases, wall=None):
    """A JUnit report of (classname, seconds) cases and its GNU time report."""
    directory.mkdir(parents=True, exist_ok=True)
    body = "".join(
        f'<testcase classname="{classname}" name="t{i}" time="{time}"/>'
        for i, (classname, time) in enumerate(cases)
    )
    (directory / f"{name}.xml").write_text(
        f'<testsuites><testsuite name="pytest">{body}</testsuite></testsuites>'
    )
    if wall is not None:
        (directory / f"{name}-resources.txt").write_text(
            "\tCommand being timed: pytest\n"
            f"\tElapsed (wall clock) time (h:mm:ss or m:ss): {wall}\n"
            "\tMaximum resident set size (kbytes): 1000\n"
        )


def test_timings_come_from_each_shards_junit_and_gnu_time_reports(tmp_path):
    files = ["pkg/tests/test_a.py", "pkg/tests/core/test_b.py", "pkg/tests/test_c.py"]
    write_report(
        tmp_path / "rest-python-test-timings-shard-1",
        "rest-python-core-1",
        [
            ("pkg.tests.test_a", 10),
            ("pkg.tests.test_a.TestClass", 5.5),
            ("pkg.tests.core.test_b", 20),
            ("pkg.tests.test_removed", 7),
        ],
        wall="1:02.5",
    )
    write_report(
        tmp_path / "rest-python-test-timings-shard-2",
        "rest-python-remaining",
        [("pkg.tests.core.test_b", 1)],
        wall="1:00:01",
    )
    write_report(tmp_path / "rest-variables-test-timings", "rest-variables", [], "1:10")
    # An earlier attempt's leftover report covers files a later shard ran
    # too: each file counts once, at its longer time, not twice.
    write_report(
        tmp_path / "rest-python-test-timings-shard-6",
        "rest-python-core-3",
        [("pkg.tests.test_a", 12), ("pkg.tests.core.test_b", 30)],
    )
    seconds, overhead, variables = shards.read_timings(tmp_path, files)
    assert seconds == {"pkg/tests/test_a.py": 15.5, "pkg/tests/core/test_b.py": 30}
    # 62.5 - 42.5 and 3601 - 1 seconds outside tests: the median of the two.
    assert overhead == pytest.approx((20 + 3600) / 2)
    assert variables == 70
    assert shards.read_timings(tmp_path / "missing", files) == ({}, None, None)


def test_the_matrix_carries_each_shards_processes_as_json():
    groups = {"a": ["a/test_0.py", "a/test_1.py"], "b": ["b/test 0's.py"]}
    plan = shards.make_plan(groups, min_shards=2)
    entries = shards.matrix(plan)["include"]
    assert [entry["shard"] for entry in entries] == [1, 2]
    assert [entry["variables"] for entry in entries] == [
        shard["variables"] for shard in plan
    ]
    assert [json.loads(entry["processes"]) for entry in entries] == [
        shard["processes"] for shard in plan
    ]


def ci_jobs(workflow):
    jobs = workflow_jobs(workflow)
    calls = [
        name
        for name, config in jobs.items()
        for step in config.get("steps", [])
        if PLANNER_COMMAND in step.get("run", "")
        or "make test-other-python-rest" in step.get("run", "")
    ]
    assert sorted(calls) == ["RestPlan", "RestPython"], (workflow.name, calls)
    return jobs


@pytest.mark.parametrize("workflow", WORKFLOWS, ids=lambda path: path.name)
def test_ci_plans_from_recent_reports_then_runs_and_uploads_each_shard(workflow):
    jobs = ci_jobs(workflow)
    plan_job, shard_job = jobs["RestPlan"], jobs["RestPython"]
    assert plan_job["permissions"] == {"actions": "read", "contents": "read"}
    assert plan_job["outputs"] == {"matrix": "${{ steps.plan.outputs.matrix }}"}
    download = single(plan_job["steps"], lambda step: step.get("id") == "timings")
    plan = single(plan_job["steps"], lambda step: step.get("id") == "plan")
    assert plan_job["steps"].index(download) < plan_job["steps"].index(plan)
    assert download["env"] == {"GH_TOKEN": "${{ github.token }}"}
    assert plan["env"] == {"TIMINGS_SOURCE": "${{ steps.timings.outputs.source }}"}
    assert shlex.split(plan["run"]) == [
        "uv",
        "run",
        "--no-sync",
        *PLANNER_COMMAND.split(),
        "plan",
        "--timings",
        "rest-timings",
        "--source",
        "$TIMINGS_SOURCE",
        "--github-output",
        "$GITHUB_OUTPUT",
        "--summary",
        "$GITHUB_STEP_SUMMARY",
    ]
    assert not any(step.get("continue-on-error") for step in plan_job["steps"])

    assert shard_job["needs"] == ["RestPlan"]
    assert shard_job["strategy"] == {
        "fail-fast": False,
        "matrix": "${{ fromJSON(needs.RestPlan.outputs.matrix) }}",
    }
    assert "${{ matrix.shard }}" in shard_job["name"]
    steps = shard_job["steps"]
    run = single(steps, lambda step: PLANNER_COMMAND in step.get("run", ""))
    assert shlex.split(run["run"]) == [
        "uv",
        "run",
        "--no-sync",
        *PLANNER_COMMAND.split(),
        "run",
        "--report-dir",
        ".",
    ]
    assert run["env"]["REST_PYTHON_PROCESSES"] == "${{ matrix.processes }}"
    assert run["if"] == KEEP_RUNNING_WITH_SYSTEM_CA
    assert_system_ca_precedes(steps, run)
    upload = single(
        steps,
        lambda step: (
            step.get("uses", "").startswith("actions/upload-artifact")
            and "rest-python-*.xml" in step["with"]["path"].split()
        ),
    )
    assert upload["if"] == "always()"
    assert (
        upload["with"]["name"] == "rest-python-test-timings-shard-${{ matrix.shard }}"
    )
    patterns = upload["with"]["path"].split()
    # Every report a planned process writes is uploaded, under a name the
    # next plan downloads and reads.
    reports = [
        f"./rest-python-{name}{suffix}"
        for name in ("core", "core-12", "remaining-heavy")
        for suffix in (".xml", "-resources.txt")
    ]
    for report in reports:
        assert any(fnmatch(os.path.normpath(report), p) for p in patterns), report
    assert fnmatch("rest-python-core-12.xml", "rest-python-*.xml")
    shard_artifact = upload["with"]["name"].replace("${{ matrix.shard }}", "12")
    assert "--pattern 'rest-python-test-timings-*'" in download["run"]
    assert fnmatch(shard_artifact, "rest-python-test-timings-*")
    assert not any(step.get("continue-on-error") for step in steps)
    if workflow.name == "push.yaml":
        for job in (plan_job, shard_job):
            assert " ".join(job["if"].split()) == RELEASE_ONLY
        assert plan_job["needs"] == "ReleaseLock"
    else:
        assert "if" not in shard_job and "if" not in plan_job
        assert "needs" not in plan_job


STUB_GH = """#!/bin/sh
echo "$*" >> "$STUB_CALLS"
case "$1 $2" in
  "run list")
    [ "$STUB_LIST" = fail ] && exit 1
    printf '%s\\n' $STUB_RUNS
    ;;
  "run download")
    for good in $STUB_GOOD; do
      if [ "$3" = "$good" ]; then
        mkdir -p "rest-timings/$3/rest-python-test-timings-shard-1"
        exit 0
      fi
    done
    mkdir -p "rest-timings/$3/partial"
    exit 1
    ;;
esac
"""


@pytest.mark.parametrize("workflow", WORKFLOWS, ids=lambda path: path.name)
@pytest.mark.parametrize(
    "runs, good, listing, source, tried",
    [
        ("101 102", "101 102", "ok", "release run 101", ["101"]),
        ("101 102", "102", "ok", "release run 102", ["101", "102"]),
        ("101 102 103 104", "104", "ok", None, ["101", "102", "103"]),
        ("", "", "ok", None, []),
        ("101", "101", "fail", None, []),
    ],
)
def test_the_timing_download_never_fails_the_plan(
    tmp_path, workflow, runs, good, listing, source, tried
):
    download = single(
        workflow_jobs(workflow)["RestPlan"]["steps"],
        lambda step: step.get("id") == "timings",
    )
    assert download["shell"] == "bash"
    stub = tmp_path / "bin" / "gh"
    stub.parent.mkdir()
    stub.write_text(STUB_GH)
    stub.chmod(0o755)
    output = tmp_path / "output.txt"
    calls = tmp_path / "calls.txt"
    calls.touch()
    env = dict(
        os.environ,
        PATH=f"{stub.parent}{os.pathsep}{os.environ['PATH']}",
        GITHUB_OUTPUT=str(output),
        GITHUB_REPOSITORY="PolicyEngine/policyengine-us",
        STUB_CALLS=str(calls),
        STUB_RUNS=runs,
        STUB_GOOD=good,
        STUB_LIST=listing,
    )
    result = subprocess.run(
        ["bash", "-e", "-c", download["run"]],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    written = output.read_text() if output.exists() else ""
    assert written == (f"source={source}\n" if source else "")
    downloads = [
        line.split()[2] for line in calls.read_text().splitlines() if "download" in line
    ]
    assert downloads == tried
    # A failed download leaves nothing for the plan to read.
    kept = sorted(p.name for p in (tmp_path / "rest-timings").glob("*"))
    assert kept == ([source.split()[-1]] if source else [])
    if not source:
        assert "::warning::No Rest Python timing reports" in result.stdout


@pytest.mark.parametrize("workflow", WORKFLOWS, ids=lambda path: path.name)
def test_variable_yaml_selection_runs_once_on_the_planned_shard(workflow):
    jobs = workflow_jobs(workflow)
    calls = [
        (job, step)
        for job, config in jobs.items()
        for step in config.get("steps", [])
        if "make test-yaml-variables" in step.get("run", "")
    ]
    assert len(calls) == 1, (workflow.name, calls)
    job, step = calls[0]
    # The plan marks exactly one shard (see the plan tests above).
    assert job == "RestPython"
    assert step["if"] == (
        "${{ !cancelled() && steps.system-ca.outcome == 'success' "
        "&& matrix.variables }}"
    )
    assert_system_ca_precedes(jobs[job]["steps"], step)
    assert shlex.split(step["run"]) == [
        "/usr/bin/time",
        "-v",
        "-o",
        "rest-variables-resources.txt",
        "uv",
        "run",
        "--no-sync",
        "make",
        "test-yaml-variables",
    ]
    (command,) = dry_run("test-yaml-variables", prefixes=("python ",))
    assert command == [
        "python",
        "policyengine_us/tests/test_batched.py",
        "policyengine_us/tests/variables",
        "--batches",
        "1",
    ]
    upload = single(
        jobs[job]["steps"],
        lambda candidate: (
            candidate.get("uses", "").startswith("actions/upload-artifact")
            and "rest-variables.xml" in candidate["with"]["path"].split()
        ),
    )
    assert upload["if"] == "${{ always() && matrix.variables }}"
    assert upload["with"]["name"] == "rest-variables-test-timings"
    download = single(
        jobs["RestPlan"]["steps"], lambda candidate: candidate.get("id") == "timings"
    )
    assert "--pattern rest-variables-test-timings" in download["run"]
    junit = [
        arg.removeprefix("--junitxml=")
        for arg in shlex.split(step["env"]["PYTEST_ADDOPTS"])
        if arg.startswith("--junitxml=")
    ]
    assert junit == ["rest-variables.xml"]
    patterns = upload["with"]["path"].split()
    assert all(
        any(fnmatch(report, pattern) for pattern in patterns)
        for report in [junit[0], "rest-variables-resources.txt"]
    )


@pytest.mark.parametrize("workflow", WORKFLOWS, ids=lambda path: path.name)
def test_original_rest_check_aggregates_the_plan_and_shards_without_hiding_failure(
    workflow,
):
    jobs = workflow_jobs(workflow)
    summary = jobs["Rest"]
    assert summary["name"] == "Full Suite - Rest (Python + variables)"
    assert summary["needs"] == ["RestPlan", "RestPython"]
    # It runs after a failed plan or shard, but a cancelled run stops it: a
    # job-level always() kept it running after cancellation.
    assert "always()" not in summary["if"]
    assert "strategy" not in summary
    assert not summary.get("continue-on-error", False)
    assert not jobs["RestPlan"].get("continue-on-error", False)
    assert not jobs["RestPython"].get("continue-on-error", False)
    if workflow.name == "push.yaml":
        assert " ".join(summary["if"].split()) == (
            "!cancelled() && (needs.RestPlan.result != 'skipped') && " + RELEASE_ONLY
        )
        assert {"RestPlan", "RestPython", "Rest"} <= set(jobs["Publish"]["needs"])
    else:
        assert summary["if"] == "${{ !cancelled() }}"
    (step,) = summary["steps"]
    assert step["shell"] == "bash"
    assert step["env"] == {
        "PLAN_RESULT": "${{ needs.RestPlan.result }}",
        "PYTHON_RESULT": "${{ needs.RestPython.result }}",
    }
    outcomes = ("success", "failure", "cancelled", "skipped")
    for plan in outcomes:
        for python in outcomes:
            env = dict(os.environ, PLAN_RESULT=plan, PYTHON_RESULT=python)
            result = subprocess.run(
                ["bash", "-e", "-c", step["run"]],
                cwd=REPO,
                env=env,
                capture_output=True,
                text=True,
            )
            assert (result.returncode == 0) == (plan == python == "success"), (
                workflow.name,
                plan,
                python,
                result.stdout + result.stderr,
            )


@pytest.mark.parametrize("workflow", WORKFLOWS, ids=lambda path: path.name)
def test_spm_and_dataset_suites_run_once_in_separate_steps_with_reports(workflow):
    jobs = yaml.safe_load(workflow.read_text())["jobs"]
    selected = []
    reports = []
    for target in ("test-other-python-spm", "test-microsimulation"):
        calls = [
            (job, step)
            for job, config in jobs.items()
            for step in config.get("steps", [])
            if target in step.get("run", "")
        ]
        assert len(calls) == 1, (target, calls)
        job, step = calls[0]
        assert job == "Microsimulation", (target, job)
        command = shlex.split(step["run"])
        assert command[:3] == ["/usr/bin/time", "-v", "-o"]
        assert command[4:] == ["uv", "run", "--no-sync", "make", target]
        assert not step.get("continue-on-error", False)
        junit = [
            arg.removeprefix("--junitxml=")
            for arg in shlex.split(step["env"]["PYTEST_ADDOPTS"])
            if arg.startswith("--junitxml=")
        ]
        assert len(junit) == 1
        reports.extend([command[3], *junit])
        selected.append(step)
    steps = jobs["Microsimulation"]["steps"]
    assert steps.index(selected[0]) < steps.index(selected[1])
    assert selected[1]["if"] == KEEP_RUNNING_WITH_SYSTEM_CA
    assert_system_ca_precedes(steps, selected[0])
    assert len(set(reports)) == 4
    uploads = [
        step
        for step in steps
        if step.get("uses", "").startswith("actions/upload-artifact")
    ]
    assert len(uploads) == 1
    assert uploads[0]["if"] == "always()"
    patterns = uploads[0]["with"]["path"].split()
    assert all(
        any(fnmatch(report, pattern) for pattern in patterns) for report in reports
    )
    assert uploads[0]["with"]["name"] != "rest-test-timings"


def test_groups_run_as_plain_pytest_without_a_report_dir(groups):
    """Locally the same groups run without GNU time, which macOS lacks."""
    plain = dry_run("test-other-python-rest")
    assert [argv[0] for argv in plain] == ["pytest"] * len(groups)
    assert [argv[1:] for argv in plain] == [spec["args"] for spec in groups.values()]


def test_an_inherited_report_dir_does_not_change_the_reference(monkeypatch, groups):
    monkeypatch.setenv("REST_REPORT_DIR", "inherited-reports")
    plain = dry_run("test-other-python-rest")
    assert [argv[1:] for argv in plain] == [spec["args"] for spec in groups.values()]
    assert shards.make_groups() == {
        group: spec["args"] for group, spec in groups.items()
    }


def import_name(file):
    """The module name pytest's default import mode gives a test file: its
    dotted path within its outermost package, or its stem outside one."""
    path = REPO / file
    parts = [path.stem]
    while (path.parent / "__init__.py").exists():
        path = path.parent
        parts.insert(0, path.name)
    return ".".join(parts)


def test_test_files_keep_distinct_import_names(reference):
    """The old single process failed on two test files with one import name
    ("import file mismatch"). Split across groups, both would pass; make
    test-other-python would still fail."""
    by_name = defaultdict(list)
    for file in reference:
        by_name[import_name(file)].append(file)
    clashes = {name: files for name, files in by_name.items() if len(files) > 1}
    assert not clashes, clashes


# Stands in for pytest on PATH: records its arguments, joined with "|" so a
# split argument shows, then exits with the next outcome in STUB_OUTCOMES, or
# kills itself with SIGKILL, as the kernel's out-of-memory killer does, for
# "killed".
STUB_PYTEST = """#!/bin/sh
(IFS='|'; echo "$*") >> "$STUB_CALLS"
n=$(wc -l < "$STUB_CALLS" | tr -d ' ')
outcome=$(echo "$STUB_OUTCOMES" | cut -d ' ' -f "$n")
if [ "$outcome" = killed ]; then kill -9 $$; fi
exit "$outcome"
"""


def stub_environment(tmp_path, outcomes):
    stub = tmp_path / "bin" / "pytest"
    stub.parent.mkdir()
    stub.write_text(STUB_PYTEST)
    stub.chmod(0o755)
    calls = tmp_path / "calls.txt"
    env = {k: v for k, v in os.environ.items() if k not in PARENT_MAKE_VARIABLES}
    env["PATH"] = f"{stub.parent}{os.pathsep}{env['PATH']}"
    env["STUB_CALLS"] = str(calls)
    env["STUB_OUTCOMES"] = " ".join(outcomes)
    return env, calls


def scenario_outcomes(scenario, count):
    outcomes = ["0"] * count
    if scenario == "one-fails-one-killed":
        assert count >= 4, "need processes before and after the failures"
        outcomes[1] = "1"
        outcomes[3] = "killed"
    elif scenario == "all-fail":
        outcomes = ["killed"] + ["1"] * (count - 1)
    return outcomes


@pytest.mark.parametrize("scenario", ["one-fails-one-killed", "all-fail", "all-pass"])
def test_every_group_runs_and_any_failure_fails_the_target(tmp_path, groups, scenario):
    outcomes = scenario_outcomes(scenario, len(groups))
    env, calls = stub_environment(tmp_path, outcomes)
    result = subprocess.run(
        ["make", "--no-print-directory", "test-other-python-rest"],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
    )
    # Every group ran, with the arguments the dry runs above check.
    ran = ["|".join(spec["args"]) for spec in groups.values()]
    assert calls.read_text().splitlines() == ran
    failed = [group for group, outcome in zip(groups, outcomes) if outcome != "0"]
    assert (result.returncode != 0) == bool(failed), result.stdout + result.stderr
    if failed:
        assert f"Failed Rest Python groups: {' '.join(failed)}" in result.stdout


@pytest.mark.parametrize("scenario", ["one-fails-one-killed", "all-fail", "all-pass"])
def test_every_planned_process_runs_and_any_failure_fails_the_shard(tmp_path, scenario):
    processes = [
        {"name": f"g{i}", "group": f"g{i}", "files": [f"g{i}/test_a.py", "t b.py"]}
        for i in range(5)
    ]
    outcomes = scenario_outcomes(scenario, len(processes))
    env, calls = stub_environment(tmp_path, outcomes)
    env["REST_PYTHON_PROCESSES"] = json.dumps(processes)
    result = subprocess.run(
        [sys.executable, str(PLANNER), "run"],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
    )
    assert calls.read_text().splitlines() == [
        "|".join([*p["files"], "--maxfail=0"]) for p in processes
    ]
    failed = [p["name"] for p, outcome in zip(processes, outcomes) if outcome != "0"]
    assert (result.returncode != 0) == bool(failed), result.stdout + result.stderr
    if failed:
        assert f"Failed Rest Python groups: {' '.join(failed)}" in result.stdout


def test_a_shard_without_processes_fails(tmp_path):
    env, calls = stub_environment(tmp_path, [])
    for value in (None, "", "[]"):
        if value is None:
            env.pop("REST_PYTHON_PROCESSES", None)
        else:
            env["REST_PYTHON_PROCESSES"] = value
        result = subprocess.run(
            [sys.executable, str(PLANNER), "run"],
            cwd=REPO,
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1, (value, result.stdout + result.stderr)
    assert not calls.exists()


def test_each_process_writes_its_own_reports_in_the_report_dir(monkeypatch):
    commands = []
    monkeypatch.setattr(
        shards.subprocess,
        "run",
        lambda command: (
            commands.append(command) or subprocess.CompletedProcess(command, 0)
        ),
    )
    processes = [
        {"name": "core-2", "group": "core", "files": ["core/test_a.py"]},
        {"name": "policy", "group": "policy", "files": ["p/test_b.py", "p/test_c.py"]},
    ]
    assert shards.run_processes(processes, ".") == 0
    assert commands == [
        [
            "/usr/bin/time",
            "-v",
            "-o",
            "./rest-python-core-2-resources.txt",
            "pytest",
            "core/test_a.py",
            "--maxfail=0",
            "--junitxml=./rest-python-core-2.xml",
        ],
        [
            "/usr/bin/time",
            "-v",
            "-o",
            "./rest-python-policy-resources.txt",
            "pytest",
            "p/test_b.py",
            "p/test_c.py",
            "--maxfail=0",
            "--junitxml=./rest-python-policy.xml",
        ],
    ]


def test_conftest_files_cannot_change_which_files_are_collected(old_command):
    """The listing skips conftest.py; that is exact only while no conftest.py
    the Rest groups load defines collection hooks, collect_ignore or plugins."""
    ignored = [
        REPO / arg.removeprefix("--ignore=")
        for arg in old_command
        if arg.startswith("--ignore=")
    ]
    conftests = [REPO / "conftest.py", REPO / "policyengine_us" / "conftest.py"]
    conftests += sorted(TESTS.rglob("conftest.py"))
    found = []
    for conftest in conftests:
        if not conftest.exists() or any(conftest.is_relative_to(p) for p in ignored):
            continue
        for node in ast.parse(conftest.read_text()).body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names = [node.name]
            elif isinstance(node, ast.Assign):
                names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names = [node.target.id]
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [alias.asname or alias.name for alias in node.names]
            else:
                names = []
            found += [
                f"{conftest.relative_to(REPO)}: {name}"
                for name in names
                if name.startswith(("pytest_", "collect_ignore"))
            ]
    assert not found, (
        "These can change which files pytest collects, which the listing in "
        f"this guard does not see; make it load conftest files: {found}"
    )


def write_test_files(root, names):
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def test_nothing():\n    pass\n")


def test_the_check_reports_a_file_outside_every_group(tmp_path):
    write_test_files(tmp_path, ["a/test_one.py", "b/test_two.py", "new/test_new.py"])
    reference = collected_files(["."], cwd=tmp_path)
    collected = {
        "a": collected_files(["a"], cwd=tmp_path),
        "b": collected_files(["b"], cwd=tmp_path),
    }
    assert partition_problems(reference, collected) == [
        "new/test_new.py is collected by no group"
    ]


def test_the_check_reports_a_file_in_two_groups(tmp_path):
    write_test_files(tmp_path, ["a/test_one.py", "b/test_two.py"])
    reference = collected_files([".", "--ignore=b"], cwd=tmp_path)
    collected = {
        "a": collected_files(["a"], cwd=tmp_path),
        "everything": collected_files(["."], cwd=tmp_path),
    }
    assert partition_problems(reference, collected) == [
        "a/test_one.py is collected by a, everything",
        "b/test_two.py is collected by everything but was not in the old "
        "single process",
    ]
