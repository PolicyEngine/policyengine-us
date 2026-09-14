"""Batch status must follow the child process, including pytest setup errors."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import signal

import pytest


SPEC = importlib.util.spec_from_file_location(
    "batch_result_runner", Path(__file__).resolve().parents[1] / "test_batched.py"
)
batched = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(batched)


def _run_child(monkeypatch, command, **batch_options):
    """Replace only the model command; retain real pipes, polling and exit codes."""
    popen = subprocess.Popen
    children = []

    def launch(_command, **kwargs):
        child = popen(command, **kwargs)
        children.append(child)
        return child

    monkeypatch.setattr(batched.subprocess, "Popen", launch)
    result = batched.run_batch(
        ["unused-by-this-child"], "process regression", stream=False, **batch_options
    )
    assert len(children) == 1
    assert children[0].poll() is not None
    return result, children[0].returncode


def test_real_pytest_setup_error_fails_batch(tmp_path, monkeypatch):
    test_file = tmp_path / "test_setup_error.py"
    test_file.write_text(
        "import pytest\n"
        "def test_pass(): pass\n"
        "@pytest.fixture\n"
        "def broken(): raise RuntimeError('setup failed')\n"
        "def test_setup(broken): pass\n"
    )
    result, returncode = _run_child(
        monkeypatch,
        [sys.executable, "-m", "pytest", "-o", "addopts=", str(test_file)],
    )
    assert returncode == 1
    assert "1 passed, 1 error" in result["output"]
    assert result["status"] == "failed"


@pytest.mark.parametrize("returncode", [0, 1, 2, 3, 4, 5])
def test_exit_status_is_authoritative_after_summary(monkeypatch, returncode):
    result, actual = _run_child(
        monkeypatch,
        [
            sys.executable,
            "-c",
            "import sys; print('===== 1 passed in 0.01s ====='); "
            f"sys.exit({returncode})",
        ],
    )
    assert actual == returncode
    assert result["status"] == ("passed" if returncode == 0 else "failed")
    assert result["returncode"] == returncode


def test_summary_does_not_terminate_running_child(monkeypatch):
    result, returncode = _run_child(
        monkeypatch,
        [
            sys.executable,
            "-c",
            "import sys, time; print('===== 1 passed in 0.01s =====', flush=True); "
            "time.sleep(1.2); print('cleanup complete'); sys.exit(3)",
        ],
    )
    assert returncode == 3
    assert "cleanup complete" in result["output"]
    assert result["status"] == "failed"


def test_clean_exit_without_summary_passes(monkeypatch):
    result, returncode = _run_child(monkeypatch, [sys.executable, "-c", "pass"])
    assert returncode == 0
    assert result["status"] == "passed"


def test_signal_exit_is_failure(monkeypatch):
    result, returncode = _run_child(
        monkeypatch,
        [
            sys.executable,
            "-c",
            "import os, signal; os.kill(os.getpid(), signal.SIGTERM)",
        ],
    )
    assert returncode == -signal.SIGTERM
    assert result["status"] == "failed"


@pytest.mark.parametrize(
    "output", ["", "print('===== 1 passed in 0.01s =====', flush=True);"]
)
def test_timeout_is_enforced_without_inventing_success(monkeypatch, output):
    result, returncode = _run_child(
        monkeypatch,
        [sys.executable, "-c", f"import time; {output} time.sleep(60)"],
        timeout_seconds=0.1,
    )
    assert returncode == -signal.SIGTERM
    assert result["status"] == "timeout"
