"""YAML batches must not rerun the separately routed Python suites.

Exercise the real Core CLI and pytest collector with a one-variable country
package, so this runner regression never constructs the full US model.
"""

import importlib.util
import os
import shlex
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

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
