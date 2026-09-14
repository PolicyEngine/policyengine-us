"""The batch runner's verdict must come from the runner's own exit status.

`test_batched.py` used to decide a batch by parsing the pytest summary line:
absent a `"N failed"` count it called the batch passed, then terminated the
child without ever reading its status. pytest prints no failure count for an
errored run, so a real child producing

    1 passed, 1 error in 0.01s          (actual exit status: 1)

was reported as a passing batch, and `make test-yaml-*` exited 0 on it.

The status cannot simply be waited for: policyengine-core takes tens of seconds
to tear down after pytest.main() returns, which is why the child is terminated
as soon as it reports. So the command runs through a shim that writes pytest's
return value to stdout the instant it has one, and the runner reads that.

Each test here drives the real `run_batch` against a real subprocess whose
output and status are scripted, so the runner's own Popen/select/terminate path
is what is under test, not a stand-in for it.
"""

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

BATCHER = Path(__file__).resolve().parents[1] / "test_batched.py"
SPEC = importlib.util.spec_from_file_location("test_batched", BATCHER)
batched = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(batched)


def scripted_child(
    summary: str,
    exit_code: int,
    then_hang: bool = False,
    report: bool = True,
):
    """A command that prints a pytest-shaped summary, then finishes as told.

    With report=True it also writes the shim's exit marker, standing in for
    the real runner; with report=False it stands in for a child that died
    before pytest could hand back a status.
    """
    body = f"import sys, time\nprint({summary!r}, flush=True)\n"
    if report:
        body += (
            f"print('{batched.BATCH_EXIT_MARKER} ' + str({exit_code}), flush=True)\n"
        )
    if then_hang:
        body += "time.sleep(600)\n"
    body += f"sys.exit({exit_code})\n"
    return [sys.executable, "-u", "-c", body]


PASSING_SUMMARY = "============ 2 passed in 0.01s ============"
# pytest prints no failure count for an errored run: this is the exact string
# from the reproduction, and the one the old parser scored as a pass.
ERRORED_SUMMARY = "============ 1 passed, 1 error in 0.01s ============"
FAILING_SUMMARY = "============ 1 failed, 1 passed in 0.01s ============"


def run_scripted(summary: str, exit_code: int, **kwargs):
    return batched.run_batch(
        ["unused/path.yaml"],
        "Batch 1",
        stream=False,
        command=scripted_child(summary, exit_code, **kwargs),
    )


def test_summary_without_a_failure_count_does_not_override_an_error_exit():
    """The reproduced defect: "1 passed, 1 error" with child exit 1."""
    result = run_scripted(ERRORED_SUMMARY, 1)
    assert result["returncode"] == 1
    assert result["status"] == "failed"


def test_a_clean_summary_still_fails_on_a_nonzero_exit():
    """Interrupted, internal-error and usage-error runs print no count either."""
    for exit_code in (2, 3, 4):
        result = run_scripted(PASSING_SUMMARY, exit_code)
        assert result["returncode"] == exit_code
        assert result["status"] == "failed", exit_code


def test_no_tests_collected_is_a_failure_for_the_batch_runner():
    """This runner enumerates the suite, so an empty batch is broken enumeration.

    `run_selective_tests.py` deliberately skips pytest's exit 5 because it
    selects paths from a changed-file list, where a changed test helper
    legitimately collects nothing. Nothing selects paths here but this file.
    """
    result = run_scripted("============ no tests ran in 0.01s ============", 5)
    assert result["returncode"] == batched.PYTEST_NO_TESTS_COLLECTED
    assert result["status"] == "failed"
    assert "collected no tests" in batched.describe_exit_status(5)


def test_a_passing_batch_still_passes():
    """The guard must not turn the ordinary green run red."""
    result = run_scripted(PASSING_SUMMARY, 0)
    assert result["returncode"] == 0
    assert result["status"] == "passed"


def test_a_reported_failure_stays_a_failure():
    result = run_scripted(FAILING_SUMMARY, 1)
    assert result["status"] == "failed"


def test_a_slow_teardown_after_a_clean_run_still_passes():
    """The real runner takes tens of seconds to exit; that is not a failure.

    Waiting the child out instead of reading its report turned every large
    green batch red: measured on this suite, a single small state took 18.2s
    to exit after its summary and the large state batches took over 30s.
    """
    result = run_scripted(PASSING_SUMMARY, 0, then_hang=True)
    assert result["returncode"] == 0
    assert result["status"] == "passed"


def test_a_slow_teardown_after_a_failed_run_still_fails():
    result = run_scripted(FAILING_SUMMARY, 1, then_hang=True)
    assert result["returncode"] == 1
    assert result["status"] == "failed"


def test_a_child_killed_before_reporting_is_not_credited_a_pass():
    """No report and a nonzero status: an OOM kill mid-run, not a pass."""
    result = run_scripted(PASSING_SUMMARY, 137, report=False)
    assert result["returncode"] == 137
    assert result["status"] == "failed"


def test_the_shim_reports_the_real_runner_status():
    """End to end against policyengine-core, not a scripted stand-in.

    An empty directory collects nothing, so pytest exits 5 - a status the
    summary line never carries and the runner now reports.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as empty:
        result = batched.run_batch([empty], "Batch 1", stream=False)
    assert batched.BATCH_EXIT_MARKER in result["output"]
    assert result["returncode"] == batched.PYTEST_NO_TESTS_COLLECTED
    assert result["status"] == "failed"


def test_a_child_that_never_prints_a_summary_is_judged_by_its_exit_status():
    """Crashes before the summary line (OOM kill, import error) still count."""
    crashing = [sys.executable, "-u", "-c", "import sys; sys.exit(1)"]
    result = batched.run_batch(
        ["unused/path.yaml"], "Batch 1", stream=False, command=crashing
    )
    assert result["status"] == "failed"

    clean = [sys.executable, "-u", "-c", "pass"]
    assert (
        batched.run_batch(["unused/path.yaml"], "Batch 1", stream=False, command=clean)[
            "status"
        ]
        == "passed"
    )


@pytest.mark.parametrize("returncode", [1, 2, 3, 4, 5, -9, -15, None])
def test_batch_status_passes_nothing_but_a_zero_exit(returncode):
    assert batched.batch_status(returncode) == "failed"


def test_batch_status_passes_a_zero_exit():
    assert batched.batch_status(0) == "passed"


# --- .yml enumeration --------------------------------------------------------
#
# policyengine-core collects both suffixes (tools/test_runner.py:413), so a
# `.yml` test omitted from a file-level batch would never run, and the batch it
# belonged to would still report green.


def write_cases(path: Path, reforms: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            [
                {
                    "name": f"{path.stem} {reform}",
                    "period": 2026,
                    "reforms": reform,
                    "input": {"people": {"person": {"age": 30}}},
                    "output": {"age": 30},
                }
                for reform in reforms
            ]
        )
    )


def test_yaml_enumeration_covers_both_suffixes(tmp_path):
    write_cases(tmp_path / "a.yaml", ["r1"])
    write_cases(tmp_path / "nested" / "b.yml", ["r2"])
    assert batched.yaml_files(tmp_path) == [
        tmp_path / "a.yaml",
        tmp_path / "nested" / "b.yml",
    ]
    assert batched.root_yaml_files(tmp_path) == [tmp_path / "a.yaml"]
    assert batched.count_yaml_files(tmp_path) == 2


def test_heavy_subdir_splitting_includes_yml_files(tmp_path):
    """The split that packs a heavy folder file by file must see every file."""
    heavy = tmp_path / "heavy"
    write_cases(heavy / "a.yaml", ["r1", "r2", "r3", "r4"])
    write_cases(heavy / "b.yml", ["r5", "r6"])
    batches = batched.subdir_batches(heavy)
    packed = {path for batch in batches for path in batch}
    assert str(heavy / "b.yml") in packed
    assert str(heavy / "a.yaml") in packed


def test_heavy_subdir_weight_counts_yml_files(tmp_path):
    """A folder pushed over budget by `.yml` files alone must still split."""
    heavy = tmp_path / "heavy"
    write_cases(heavy / "a.yml", ["r1", "r2", "r3", "r4"])
    write_cases(heavy / "b.yml", ["r5", "r6"])
    assert batched.subdir_batches(heavy) != [[str(heavy)]]


def test_per_file_mode_includes_yml_files(tmp_path):
    write_cases(tmp_path / "a.yaml", ["r1"])
    write_cases(tmp_path / "b.yml", ["r2"])
    batches = batched.split_into_batches(tmp_path, 2, mode="per-file")
    assert batches == [[str(tmp_path / "a.yaml")], [str(tmp_path / "b.yml")]]


def test_per_subdir_mode_collects_root_yml_files(tmp_path):
    write_cases(tmp_path / "light" / "a.yaml", ["r1"])
    write_cases(tmp_path / "root.yml", ["r2"])
    batches = batched.split_into_batches(tmp_path, 2, mode="per-subdir")
    assert batches == [[str(tmp_path / "light")], [str(tmp_path / "root.yml")]]


def test_default_split_and_exclude_branches_include_yml_files(tmp_path):
    write_cases(tmp_path / "keep" / "a.yml", ["r1"])
    write_cases(tmp_path / "drop" / "b.yaml", ["r2"])
    write_cases(tmp_path / "root.yml", ["r3"])
    assert batched.split_into_batches(tmp_path, 1, exclude=["drop"]) == [
        [str(tmp_path / "keep"), str(tmp_path / "root.yml")]
    ]
    assert batched.split_into_batches(tmp_path, 2) == [
        [str(tmp_path / "drop" / "b.yaml"), str(tmp_path / "keep" / "a.yml")],
        [str(tmp_path / "root.yml")],
    ]


# --- The monitoring loop is bounded ------------------------------------------
#
# The loop ends when the child exits or reports, and nothing else. The 30-minute
# batch budget sat below it, where the child had already gone and the wait it
# guarded returned instantly, so it never fired. Reading the status from the
# runner rather than terminating a second after the summary also opened a
# second window: pytest's session-finish hooks, between the summary line and
# pytest.main() returning. Both are bounded inside the loop now.


def test_a_child_that_never_reports_after_its_summary_is_abandoned(monkeypatch):
    """Not a hang: terminated, and reported as the failure it is."""
    monkeypatch.setattr(batched, "MARKER_GRACE_SECONDS", 1)
    result = run_scripted(PASSING_SUMMARY, 0, then_hang=True, report=False)
    assert result["status"] == "failed"
    assert "No status" in result["output"]


def test_a_child_that_never_says_anything_hits_the_batch_budget(monkeypatch):
    """The 30-minute budget the runner documents now actually fires."""
    monkeypatch.setattr(batched, "BATCH_TIMEOUT_SECONDS", 1)
    silent = [sys.executable, "-u", "-c", "import time; time.sleep(600)"]
    result = batched.run_batch(
        ["unused/path.yaml"], "Batch 1", stream=False, command=silent
    )
    assert result["status"] == "timeout"
    assert "Timeout" in result["output"]
    # main() counts anything but "passed" as a failure.
    assert result["status"] != "passed"


def test_the_bounds_do_not_fire_on_an_ordinary_run():
    """A batch that reports promptly is untouched by either bound."""
    result = run_scripted(PASSING_SUMMARY, 0)
    assert result["status"] == "passed"
    assert "Timeout" not in result["output"]
    assert "No status" not in result["output"]
