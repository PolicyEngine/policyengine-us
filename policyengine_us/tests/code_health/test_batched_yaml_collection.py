"""YAML batches must not rerun the separately routed Python suites, and must
continue in a fresh subprocess once one passes the memory budget.

Exercise the real Core CLI and pytest collector with a one-variable country
package, so these runner regressions never construct the full US model.
"""

import importlib.util
import os
import re
import shlex
import subprocess
import sys
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
