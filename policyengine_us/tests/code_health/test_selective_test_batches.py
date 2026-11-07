"""Selective reform folders must release model caches between test files.

Record the real runner's child commands without constructing a US model. The
folder route must keep both YAML suffixes and Python tests, append coverage
across sequential children, and preserve failures while running later files.
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


RUNNER_PATH = Path(__file__).resolve().parents[1] / "run_selective_tests.py"
REPO = Path(__file__).resolve().parents[3]


def test_direct_script_imports_the_batcher_without_loading_a_model(tmp_path):
    (tmp_path / "policyengine_us.py").write_text(
        "raise AssertionError('The selective runner must not import the model')\n"
    )
    result = subprocess.run(
        [sys.executable, str(RUNNER_PATH), "--help"],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(tmp_path)},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "--coverage" in result.stdout


@pytest.fixture
def selective(monkeypatch):
    # Loading by filename keeps policyengine_us.__init__ (and its full model)
    # out of these tooling tests. Direct CLI execution uses this same import.
    monkeypatch.syspath_prepend(str(RUNNER_PATH.parent))
    spec = importlib.util.spec_from_file_location(
        "selective_runner_for_batch_tests", RUNNER_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_files(paths):
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")


def record_children(monkeypatch, selective, outcomes=None):
    commands = []

    def run(command, *args, **kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=(outcomes or {}).get(command[-1], 0))

    monkeypatch.setattr(selective.subprocess, "run", run)
    return commands


@pytest.mark.parametrize("relative", ["contrib/crfb", "reform"])
@pytest.mark.parametrize("with_coverage", [False, True])
def test_reform_folders_run_each_yaml_and_python_file_separately(
    tmp_path, monkeypatch, selective, relative, with_coverage
):
    monkeypatch.chdir(tmp_path)
    target = Path("policyengine_us/tests/policy") / relative
    files = [
        target / "alpha.yaml",
        target / "nested" / "beta.yml",
        target / "nested" / "legacy_test.py",
        target / "test_python.py",
    ]
    write_files([*files, target / "support.py"])
    runner = selective.SelectiveTestRunner()
    expected = [[str(file)] for file in files]
    assert runner.get_test_batches(str(target)) == expected

    commands = record_children(monkeypatch, selective)
    source = (
        "policyengine_us/reforms/crfb/reform.py"
        if relative == "contrib/crfb"
        else "policyengine_us/reforms/custom_reform.py"
    )
    assert (
        runner.run_tests(
            {str(target)},
            with_coverage=with_coverage,
            changed_files={source} if with_coverage else None,
        )
        == 0
    )
    assert [command[-1:] for command in commands] == expected
    for command in commands:
        assert command[0] == sys.executable
        assert command[-5:-1] == [
            "policyengine_core.scripts.policyengine_command",
            "test",
            "-c",
            "policyengine_us",
        ]
        if with_coverage:
            assert command[1:6] == ["-m", "coverage", "run", "-a", "--branch"]
            assert command[command.index("--include") + 1] == source
        else:
            assert "coverage" not in command


@pytest.mark.parametrize(
    "relative",
    ["baseline/gov/irs", "contrib_extra", "reform_extra"],
)
def test_other_folders_keep_the_existing_directory_target(
    tmp_path, monkeypatch, selective, relative
):
    monkeypatch.chdir(tmp_path)
    target = Path("policyengine_us/tests/policy") / relative
    write_files([target / "a.yaml", target / "b.yml", target / "test_python.py"])
    runner = selective.SelectiveTestRunner()
    assert runner.get_test_batches(str(target)) == [[str(target)]]

    commands = record_children(monkeypatch, selective)
    assert runner.run_tests({str(target)}) == 0
    assert [command[-1] for command in commands] == [str(target)]


@pytest.mark.parametrize("name", ["a.yaml", "b.yml", "support.py"])
def test_direct_file_targets_are_unchanged(tmp_path, monkeypatch, selective, name):
    monkeypatch.chdir(tmp_path)
    target = Path("policyengine_us/tests/policy/contrib/crfb") / name
    write_files([target])
    runner = selective.SelectiveTestRunner()
    assert runner.get_test_batches(str(target)) == [[str(target)]]

    commands = record_children(monkeypatch, selective)
    assert runner.run_tests({str(target)}) == 0
    assert [command[-1] for command in commands] == [str(target)]


def test_absolute_reform_folder_paths_are_split(tmp_path, monkeypatch, selective):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "policyengine_us/tests/policy/contrib/crfb"
    files = [target / "a.yaml", target / "nested" / "b.yml"]
    write_files(files)
    assert selective.SelectiveTestRunner.get_test_batches(str(target)) == [
        [str(file)] for file in files
    ]


def test_missing_folder_target_is_unchanged(tmp_path, monkeypatch, selective):
    monkeypatch.chdir(tmp_path)
    target = "policyengine_us/tests/policy/contrib/missing"
    assert selective.SelectiveTestRunner.get_test_batches(target) == [[target]]


@pytest.mark.parametrize("failure", [1, -9])
def test_split_folders_keep_failures_and_run_every_later_file(
    tmp_path, monkeypatch, selective, failure
):
    monkeypatch.chdir(tmp_path)
    target = Path("policyengine_us/tests/policy/contrib/crfb")
    files = [target / "a.yaml", target / "b.yml", target / "c.yaml"]
    write_files(files)
    commands = record_children(
        monkeypatch,
        selective,
        {str(files[0]): failure, str(files[1]): selective.PYTEST_NO_TESTS_COLLECTED},
    )

    assert selective.SelectiveTestRunner().run_tests({str(target)}) == failure
    assert [command[-1] for command in commands] == [str(file) for file in files]


def test_changed_support_module_collecting_nothing_still_succeeds(
    tmp_path, monkeypatch, selective
):
    monkeypatch.chdir(tmp_path)
    support = Path("policyengine_us/tests/policy/contrib/crfb/support.py")
    write_files([support])
    commands = record_children(
        monkeypatch, selective, {str(support): selective.PYTEST_NO_TESTS_COLLECTED}
    )

    assert selective.SelectiveTestRunner().run_tests({str(support)}) == 0
    assert [command[-1] for command in commands] == [str(support)]


def test_support_only_folder_has_no_test_batches(tmp_path, monkeypatch, selective):
    monkeypatch.chdir(tmp_path)
    target = Path("policyengine_us/tests/policy/contrib/support_only")
    write_files([target / "support.py"])
    commands = record_children(monkeypatch, selective)
    runner = selective.SelectiveTestRunner()

    assert runner.get_test_batches(str(target)) == []
    assert runner.run_tests({str(target)}) == 0
    assert commands == []


def test_crfb_reform_route_runs_the_selected_folder_per_file(monkeypatch, selective):
    monkeypatch.chdir(REPO)
    source = "policyengine_us/reforms/crfb/tax_employer_payroll_tax.py"
    target = "policyengine_us/tests/policy/contrib/crfb"
    runner = selective.SelectiveTestRunner()
    runner.max_test_targets = 100
    runner.max_test_files = 10000
    selected = runner.limit_test_paths(runner.map_files_to_tests({source}), {source})
    assert selected == {target}

    files = sorted(
        path
        for path in Path(target).rglob("*")
        if path.is_file() and path.suffix in (".yaml", ".yml")
    )
    assert len(files) > 1
    commands = record_children(monkeypatch, selective)
    assert runner.run_tests(selected) == 0
    assert [command[-1] for command in commands] == [str(file) for file in files]
