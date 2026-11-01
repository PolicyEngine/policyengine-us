"""YAML batches must not rerun the separately routed Python suites, must
continue in a fresh subprocess once one passes the memory budget, and share a
runner only while its memory allows.

Exercise the real Core CLI and pytest collector with a one-variable country
package, so these runner regressions never construct the full US model.
Admission and eviction run against a scripted memory reading and stand-in
processes.
"""

import importlib.util
import io
import os
import re
import shlex
import subprocess
import sys
import threading
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import yaml

BATCHER = Path(__file__).resolve().parents[1] / "test_batched.py"
SPEC = importlib.util.spec_from_file_location("test_batched", BATCHER)
batched = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(batched)


@pytest.fixture
def small_country(tmp_path, monkeypatch):
    # The shim still uses its normal country name, resolved from the child cwd.
    (tmp_path / "policyengine_us.py").write_text(
        """
from policyengine_core.entities import Entity
from policyengine_core.parameters import ParameterNode
from policyengine_core.periods import YEAR
from policyengine_core.taxbenefitsystems import TaxBenefitSystem
from policyengine_core.variables import Variable

person = Entity("person", "people", "Person", "")

class age(Variable):
    label = "Age"
    value_type = int
    entity = person
    definition_period = YEAR

class CountryTaxBenefitSystem(TaxBenefitSystem):
    def __init__(self):
        super().__init__([person])
        self.parameters = ParameterNode("", data={})
        self.add_variable(age)
"""
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    monkeypatch.setenv("PYTEST_ADDOPTS", "")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_python.py").write_text(
        "from pathlib import Path\n"
        "Path('python-imported').touch()\n"
        "def test_python():\n"
        "    assert True\n"
    )
    return tests


def test_directory_batch_collects_yaml_only(small_country, monkeypatch):
    tests = small_country
    (tests / "nested").mkdir()
    for path in (tests / "a.yaml", tests / "nested" / "b.yml"):
        path.write_text(
            "- name: age input\n"
            "  period: 2026\n"
            "  input: {age: 30}\n"
            "  output: {age: 30}\n"
        )
    (tests / "conftest.py").write_text(
        "from pathlib import Path\nPath('conftest-loaded').touch()\n"
    )
    report = tests.parent / "yaml report.xml"
    inherited_options = f"-q --junitxml={shlex.quote(str(report))}"
    monkeypatch.setenv("PYTEST_ADDOPTS", inherited_options)

    result = batched.run_batch([str(tests)], "mixed directory", stream=False)

    assert result["status"] == "passed", result["output"]
    cases = ET.parse(report).findall(".//testcase")
    assert len(cases) == 2, result["output"]
    assert not (tests.parent / "python-imported").exists()
    assert (tests.parent / "conftest-loaded").exists()
    assert os.environ["PYTEST_ADDOPTS"] == inherited_options

    # The ordinary Python step must still collect and run the same file.
    python_step = subprocess.run(
        [sys.executable, "-m", "pytest", str(tests / "test_python.py")],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert python_step.returncode == 0, python_step.stdout + python_step.stderr
    assert len(ET.parse(report).findall(".//testcase")) == 1
    assert (tests.parent / "python-imported").exists()


def test_python_only_directory_is_not_a_passing_yaml_batch(small_country):
    result = batched.run_batch([str(small_country)], "no YAML", stream=False)
    assert result["returncode"] == batched.PYTEST_NO_TESTS_COLLECTED, result["output"]
    assert result["status"] == "failed"
    assert not (small_country.parent / "python-imported").exists()


def test_python_only_subdir_does_not_create_a_yaml_batch(small_country):
    assert batched.split_into_batches(small_country.parent, 2, mode="per-subdir") == []


def _write_age_cases(path, count, failing=0):
    """`count` cases for one person's age; the first `failing` of them fail."""
    path.write_text(
        yaml.safe_dump(
            [
                {
                    "name": f"{path.stem} {i}",
                    "period": 2026,
                    "input": {"age": 30},
                    "output": {"age": 31 if i < failing else 30},
                }
                for i in range(count)
            ]
        )
    )


def _part_summaries(output):
    return re.findall(r"=+ ((?:\d+ failed, )?\d+ passed)", output)


def test_memory_budget_continues_unstarted_files_in_fresh_subprocesses(
    small_country, monkeypatch
):
    for name in ("a", "b", "c"):
        _write_age_cases(small_country / f"{name}.yaml", 2)
    # Every process is past a zero budget, so each file gets its own part.
    monkeypatch.setenv(batched.MEMORY_BUDGET_ENV, "0")
    report = small_country.parent / "report.xml"
    monkeypatch.setenv("PYTEST_ADDOPTS", f"--junitxml={report}")

    result = batched.run_batch([str(small_country)], "budget", stream=False)

    assert result["status"] == "passed", result["output"]
    assert result["parts"] == 3, result["output"]
    # Each file ran exactly once, both of its cases, with none repeated.
    assert _part_summaries(result["output"]) == ["2 passed"] * 3, result["output"]
    # Every part rewrites the inherited report; the batch merges them back.
    assert len(ET.parse(report).findall(".//testcase")) == 6


def test_memory_budget_leaves_a_batch_under_it_in_one_subprocess(
    small_country, monkeypatch
):
    for name in ("a", "b", "c"):
        _write_age_cases(small_country / f"{name}.yaml", 2)
    monkeypatch.delenv(batched.MEMORY_BUDGET_ENV, raising=False)

    result = batched.run_batch([str(small_country)], "budget", stream=False)

    assert result["status"] == "passed", result["output"]
    assert result["parts"] == 1, result["output"]
    assert _part_summaries(result["output"]) == ["6 passed"], result["output"]


def test_memory_budget_never_splits_a_file(small_country, monkeypatch):
    _write_age_cases(small_country / "a.yaml", 3)
    monkeypatch.setenv(batched.MEMORY_BUDGET_ENV, "0")

    result = batched.run_batch([str(small_country)], "budget", stream=False)

    assert result["parts"] == 1, result["output"]
    assert _part_summaries(result["output"]) == ["3 passed"], result["output"]


def test_a_failure_before_the_budget_stop_fails_the_batch_but_runs_the_rest(
    small_country, monkeypatch
):
    _write_age_cases(small_country / "a.yaml", 2, failing=1)
    for name in ("b", "c"):
        _write_age_cases(small_country / f"{name}.yaml", 2)
    monkeypatch.setenv(batched.MEMORY_BUDGET_ENV, "0")

    result = batched.run_batch([str(small_country)], "budget", stream=False)

    assert result["status"] == "failed", result["output"]
    assert result["returncode"] != 0
    assert _part_summaries(result["output"]) == [
        "1 failed, 1 passed",
        "2 passed",
        "2 passed",
    ], result["output"]


WAIT = 5


@pytest.fixture
def memory(monkeypatch):
    """The runner's available memory, set by each test."""
    reading = {"mb": 16000.0}
    monkeypatch.setattr(batched, "available_mb", lambda: reading["mb"])
    monkeypatch.setattr(batched, "ADMIT_STAGGER_SECONDS", 0)
    return reading


@pytest.fixture
def admission():
    gate = batched.Admission()
    yield gate
    gate.stopped = True


class Process:
    def __init__(self):
        self.killed = threading.Event()

    def kill(self):
        self.killed.set()


class Worker:
    """A thread holding one admission slot, rerunning alone if stopped.

    As in run_batch, a stopped part's own thread asks for the exclusive slot.
    """

    def __init__(self, admission, process=None):
        self.admitted = threading.Event()
        self.go = threading.Event()
        self.released = threading.Event()
        self.rerun_start = threading.Event()
        self.rerun_admitted = threading.Event()
        self.rerun_go = threading.Event()
        self.evicted = None

        def run():
            admission.acquire(False)
            if process is not None:
                admission.started(process)
            self.admitted.set()
            self.go.wait(WAIT * 4)
            self.evicted = admission.release()
            self.released.set()
            if self.evicted:
                self.rerun_start.wait(WAIT * 4)
                admission.acquire(True)
                self.rerun_admitted.set()
                self.rerun_go.wait(WAIT * 4)
                admission.release()

        threading.Thread(target=run, daemon=True).start()


def test_parent_reads_the_runners_available_memory(monkeypatch):
    def reading(text):
        monkeypatch.setattr(
            batched, "open", lambda *args, **kwargs: io.StringIO(text), raising=False
        )
        return batched.available_mb()

    assert reading("MemTotal: 16384000 kB\nMemAvailable:    8192000 kB\n") == 8000.0
    assert reading("MemTotal: 16384000 kB\n") is None
    assert reading("MemAvailable: junk kB\n") is None

    def missing(*args, **kwargs):
        raise OSError

    monkeypatch.setattr(batched, "open", missing, raising=False)
    assert batched.available_mb() is None


def test_one_subprocess_at_a_time_when_memory_cannot_be_read(admission, memory):
    memory["mb"] = None
    admission.acquire(False)
    second = Worker(admission)
    assert not second.admitted.wait(1)
    admission.release()
    assert second.admitted.wait(WAIT)
    second.go.set()


def test_another_subprocess_starts_only_with_memory_to_spare(admission, memory):
    admission.acquire(False)
    memory["mb"] = batched.ADMIT_MB - 1
    second = Worker(admission)
    assert not second.admitted.wait(1.5)
    memory["mb"] = batched.ADMIT_MB
    assert second.admitted.wait(WAIT)
    assert admission.waits == 1
    second.go.set()


def test_subprocesses_start_one_stagger_apart(admission, memory, monkeypatch):
    monkeypatch.setattr(batched, "ADMIT_STAGGER_SECONDS", 1.5)
    admission.acquire(False)
    second = Worker(admission)
    assert not second.admitted.wait(0.75)
    assert second.admitted.wait(WAIT)
    second.go.set()


def test_low_memory_stops_the_newest_and_admits_nothing_until_its_rerun(
    admission, memory
):
    older_process, newer_process = Process(), Process()
    older = Worker(admission, process=older_process)
    assert older.admitted.wait(WAIT)
    time.sleep(0.05)
    newer = Worker(admission, process=newer_process)
    assert newer.admitted.wait(WAIT)

    memory["mb"] = batched.EVICT_MB - 1
    assert newer_process.killed.wait(WAIT)
    assert not older_process.killed.is_set()
    memory["mb"] = 16000.0
    newer.go.set()
    assert newer.released.wait(WAIT)
    assert newer.evicted is True

    # Nothing new starts between the stop and the rerun, nor during the rerun.
    other = Worker(admission)
    assert not other.admitted.wait(1)
    newer.rerun_start.set()
    assert not newer.rerun_admitted.wait(1)  # the older one is still running
    older.go.set()
    assert newer.rerun_admitted.wait(WAIT)
    assert not other.admitted.wait(1)
    newer.rerun_go.set()
    assert other.admitted.wait(WAIT)
    other.go.set()
    assert older.evicted is False
    assert admission.evictions == 1


def test_a_lone_subprocess_is_never_stopped(admission, memory):
    process = Process()
    admission.acquire(False)
    admission.started(process)
    memory["mb"] = 1.0
    assert not process.killed.wait(1)
    assert admission.release() is False


def test_a_subprocess_that_has_reported_is_not_stopped(admission, memory):
    older, newer = Process(), Process()
    admission.acquire(False)
    admission.started(older)

    def report():
        admission.acquire(False)
        admission.started(newer)
        admission.finished()

    thread = threading.Thread(target=report, daemon=True)
    thread.start()
    thread.join(WAIT)
    memory["mb"] = 1.0
    assert not newer.killed.wait(1)
    assert not older.killed.is_set()


def test_split_into_one_batch_per_worker_keeps_whole_files(tmp_path):
    folder = tmp_path / "suite"
    (folder / "nested").mkdir(parents=True)
    files = [folder / "a.yaml", folder / "b.yaml", folder / "nested" / "c.yml"]
    for file in files:
        file.write_text("[]\n")
    batches = batched.fill_workers([[str(folder)]], 2)
    assert sorted(len(batch) for batch in batches) == [1, 2]
    assert sorted(path for batch in batches for path in batch) == sorted(
        str(file) for file in files
    )
    two = [str(files[0]), str(files[1])]
    assert sorted(len(batch) for batch in batched.fill_workers([two], 2)) == [1, 1]
    assert batched.fill_workers([[str(files[0])]], 2) == [[str(files[0])]]


def test_split_keeps_no_batches_and_a_folder_without_yaml(tmp_path):
    assert batched.fill_workers([], 2) == []
    empty = tmp_path / "python-only"
    empty.mkdir()
    (empty / "test_x.py").write_text("")
    # Kept as the folder, so the subprocess still exits 5 (no tests collected)
    # and fails the batch, as it does with one worker.
    assert batched.fill_workers([[str(empty)]], 2) == [[str(empty)]]


class Gate:
    """Stands in for Admission in run_batch; release() reports evictions."""

    def __init__(self, evictions=()):
        self.calls = []
        self.processes = []
        self.evictions = list(evictions)
        self.forgotten = 0

    def acquire(self, exclusive):
        self.calls.append(exclusive)

    def started(self, process):
        self.processes.append(process)

    def finished(self):
        pass

    def forget(self):
        self.forgotten = self.forgotten + 1

    def release(self):
        return self.evictions.pop(0) if self.evictions else False


def _scripted(flag, first_run_reports):
    """A part that is stopped (or reports) on its first run, passes after."""
    first = (
        f"    print({batched.BATCH_EXIT_MARKER!r} + ' 0', flush=True)\n"
        if first_run_reports
        else "    os.kill(os.getpid(), signal.SIGKILL)\n"
    )
    return [
        sys.executable,
        "-c",
        "import os, pathlib, signal, time\n"
        f"flag = pathlib.Path({str(flag)!r})\n"
        "if not flag.exists():\n"
        "    flag.touch()\n"
        "    print('==== 1 passed in 0.10s ====', flush=True)\n"
        + first
        + "    time.sleep(30)\n"
        "print('==== 2 passed in 0.10s ====')\n"
        f"print({batched.BATCH_EXIT_MARKER!r} + ' 0', flush=True)\n",
    ]


def test_an_evicted_part_reruns_alone_and_counts_once(small_country, monkeypatch):
    gate = Gate(evictions=[True])
    monkeypatch.setattr(batched, "ADMISSION", gate)
    command = _scripted(small_country / "first-run", first_run_reports=False)
    result = batched.run_batch(["a.yaml"], "evicted", stream=False, command=command)
    assert gate.calls == [False, True]
    assert len(gate.processes) == 2
    assert all(hasattr(process, "kill") for process in gate.processes)
    assert result["status"] == "passed", result["output"]
    assert result["parts"] == 1
    assert "rerunning its 1 files alone" in result["output"]


def test_a_part_stopped_after_it_reported_keeps_its_result(small_country, monkeypatch):
    # The watchdog can pick a part just as it reports; its result stands and
    # its rerun reservation is dropped, so admission is not held forever.
    gate = Gate(evictions=[True])
    monkeypatch.setattr(batched, "ADMISSION", gate)
    command = _scripted(small_country / "first-run", first_run_reports=True)
    result = batched.run_batch(["a.yaml"], "reported", stream=False, command=command)
    assert gate.calls == [False]
    assert gate.forgotten == 1
    assert result["parts"] == 1
    assert "rerunning" not in result["output"]


def _run_batcher(small_country, *args, workers=None):
    # The runner checks it is started from the repository root.
    (small_country.parent / "policyengine_us").mkdir(exist_ok=True)
    env = dict(os.environ)
    if workers is not None:
        env[batched.WORKERS_ENV] = workers
    run = subprocess.run(
        [sys.executable, str(BATCHER), str(small_country), *args],
        capture_output=True,
        text=True,
        timeout=600,
        env=env,
        cwd=small_country.parent,
    )
    return run.returncode, run.stdout + run.stderr


def test_workers_variable_runs_every_case_and_keeps_failures(small_country):
    for name in ("a", "b", "c"):
        _write_age_cases(
            small_country / f"{name}.yaml", 2, failing=1 if name == "b" else 0
        )
    code, output = _run_batcher(small_country, "--batches", "1", workers="2")
    assert code == 1, output
    assert "Workers: 2" in output
    assert "Split into 2 batches for 2 workers" in output
    assert "[memory] admission waits:" in output
    passed = sum(int(n) for n in re.findall(r"(\d+) passed", output))
    failed = sum(int(n) for n in re.findall(r"(\d+) failed", output))
    assert (passed, failed) == (5, 1), output


def test_plain_workers_flag_keeps_running_its_batches_at_once(small_country):
    for name in ("a", "b"):
        (small_country / name).mkdir()
        _write_age_cases(small_country / name / "x.yaml", 1)
    code, output = _run_batcher(small_country, "--mode", "per-subdir", "--workers", "2")
    assert code == 0, output
    assert "Running 2 batches with 2 workers" in output
    assert "[memory]" not in output
    assert "Split into" not in output


@pytest.mark.skipif(
    not Path("/proc/meminfo").exists(), reason="reads the runner's MemAvailable"
)
def test_low_runner_memory_hands_off_at_file_boundaries(small_country, monkeypatch):
    for name in ("a", "b", "c"):
        _write_age_cases(small_country / f"{name}.yaml", 2)
    monkeypatch.setattr(batched, "ADMISSION", Gate())
    monkeypatch.setattr(batched, "FLOOR_MB", 10**9)
    files = sorted(str(f) for f in small_country.glob("*.yaml"))
    result = batched.run_batch(files, "floor", stream=False)
    assert result["status"] == "passed", result["output"]
    assert result["parts"] == 3
    assert "runner available" in result["output"]
    assert "or runner floor" in result["output"]
