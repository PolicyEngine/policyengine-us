from types import SimpleNamespace

from policyengine_us.tests import run_selective_tests
from policyengine_us.tests.run_selective_tests import SelectiveTestRunner


def test_changed_yaml_tests_are_selected_directly():
    runner = SelectiveTestRunner()

    test_paths = runner.map_files_to_tests(
        {
            "policyengine_us/tests/policy/baseline/gov/irs/payroll/employer_payroll_tax.yaml",
            "policyengine_us/tests/run_selective_tests.py",
        }
    )

    assert (
        "policyengine_us/tests/policy/baseline/gov/irs/payroll/employer_payroll_tax.yaml"
        in test_paths
    )
    assert "policyengine_us/tests/run_selective_tests.py" not in test_paths


def test_runner_unit_test_is_not_treated_as_infrastructure():
    runner = SelectiveTestRunner()

    assert runner.is_test_infrastructure_file(
        "policyengine_us/tests/run_selective_tests.py"
    )
    assert not runner.is_test_infrastructure_file(
        "policyengine_us/tests/core/test_run_selective_tests.py"
    )


def test_yaml_only_changes_do_not_request_python_coverage():
    assert (
        SelectiveTestRunner.get_changed_python_coverage_patterns(
            {
                "policyengine_us/parameters/gov/states/nm/tax/income/modified_gross_income.yaml",
                "policyengine_us/tests/policy/baseline/gov/states/nm/tax/income/nm_modified_gross_income.yaml",
            }
        )
        == []
    )


def test_changed_tests_are_not_coverage_targets():
    assert SelectiveTestRunner.get_changed_python_coverage_patterns(
        {
            "policyengine_us/tests/core/test_run_selective_tests.py",
            "policyengine_us/variables/gov/states/nm/tax/income/nm_modified_gross_income.py",
        }
    ) == [
        "policyengine_us/variables/gov/states/nm/tax/income/nm_modified_gross_income.py"
    ]


def test_limit_test_paths_prefers_directly_changed_tests_for_broad_changes():
    runner = SelectiveTestRunner()
    runner.max_test_targets = 1
    runner.max_test_files = 1

    changed_files = {
        "policyengine_us/tests/policy/baseline/gov/irs/payroll/employer_payroll_tax.yaml",
        "policyengine_us/variables/gov/irs/tax/payroll/employer_payroll_tax.py",
        "policyengine_us/variables/gov/states/ca/tax/payroll/unemployment/ca_employer_state_unemployment_tax.py",
        "policyengine_us/variables/gov/states/tx/tax/payroll/unemployment/tx_employer_state_unemployment_tax.py",
    }

    limited_paths = runner.limit_test_paths(
        runner.map_files_to_tests(changed_files), changed_files
    )

    assert limited_paths == {
        "policyengine_us/tests/policy/baseline/gov/irs/payroll/employer_payroll_tax.yaml"
    }


def test_limit_test_paths_can_defer_to_full_suite_when_no_changed_tests_exist():
    runner = SelectiveTestRunner()
    runner.max_test_targets = 1
    runner.max_test_files = 1

    changed_files = {
        "policyengine_us/variables/gov/irs/tax/payroll/employer_payroll_tax.py",
        "policyengine_us/variables/gov/states/ca/tax/payroll/unemployment/ca_employer_state_unemployment_tax.py",
    }

    limited_paths = runner.limit_test_paths(
        runner.map_files_to_tests(changed_files), changed_files
    )

    assert limited_paths == set()


def test_limit_test_paths_defers_slow_ssa_baseline_directory():
    runner = SelectiveTestRunner()

    changed_files = {
        "policyengine_us/variables/gov/ssa/ss/social_security_retirement.py",
    }

    limited_paths = runner.limit_test_paths(
        runner.map_files_to_tests(changed_files), changed_files
    )

    assert "policyengine_us/tests/policy/baseline/gov/ssa" not in limited_paths
    assert limited_paths == set()


def test_limit_test_paths_defers_slow_household_directories():
    runner = SelectiveTestRunner()

    changed_files = {
        "policyengine_us/variables/household/income/person/fsla_overtime_premium.py",
        "policyengine_us/tests/policy/baseline/gov/irs/income/exemptions/fsla_overtime_premium.yaml",
    }

    limited_paths = runner.limit_test_paths(
        runner.map_files_to_tests(changed_files), changed_files
    )

    assert "policyengine_us/tests/microsimulation" not in limited_paths
    assert "policyengine_us/tests/policy/baseline/household" not in limited_paths
    assert limited_paths == {
        "policyengine_us/tests/policy/baseline/gov/irs/income/exemptions/fsla_overtime_premium.yaml",
    }


def test_limit_test_paths_keeps_direct_tests_when_deferring_slow_directory():
    runner = SelectiveTestRunner()

    changed_files = {
        "policyengine_us/reforms/ssa/trustees_core_thresholds.py",
        "policyengine_us/tests/policy/contrib/ssa/test_trustees_core_thresholds.py",
        "policyengine_us/variables/gov/ssa/ss/social_security_retirement.py",
    }

    limited_paths = runner.limit_test_paths(
        runner.map_files_to_tests(changed_files), changed_files
    )

    assert "policyengine_us/tests/policy/baseline/gov/ssa" not in limited_paths
    assert "policyengine_us/tests/policy/reform" not in limited_paths
    assert limited_paths == {
        "policyengine_us/tests/policy/contrib/ssa",
        "policyengine_us/tests/policy/contrib/ssa/test_trustees_core_thresholds.py",
    }


def test_limit_test_paths_ignores_deleted_direct_tests():
    runner = SelectiveTestRunner()

    deleted_test = (
        "policyengine_us/tests/policy/baseline/gov/ssa/social_security/"
        "social_security_retirement_reported.yaml"
    )
    existing_test = (
        "policyengine_us/tests/policy/baseline/gov/ssa/social_security/"
        "social_security_retirement.yaml"
    )
    changed_files = {
        deleted_test,
        existing_test,
        "policyengine_us/variables/gov/ssa/ss/social_security_retirement.py",
    }

    limited_paths = runner.limit_test_paths(
        runner.map_files_to_tests(changed_files), changed_files
    )

    assert deleted_test not in limited_paths
    assert existing_test in limited_paths


def _fake_pytest(returncodes):
    def run(cmd, *args, **kwargs):
        return SimpleNamespace(returncode=returncodes[cmd[-1]])

    return run


def test_paths_that_collect_no_tests_do_not_fail_the_run(monkeypatch):
    """A changed support module under tests/ collects nothing; that is not a failure."""
    runner = SelectiveTestRunner()
    monkeypatch.setattr(
        run_selective_tests.subprocess,
        "run",
        _fake_pytest({"tests/a_test.py": 0, "tests/populace_fixture.py": 5}),
    )
    assert runner.run_tests({"tests/a_test.py", "tests/populace_fixture.py"}) == 0


def test_real_failures_still_fail_beside_an_empty_path(monkeypatch):
    runner = SelectiveTestRunner()
    monkeypatch.setattr(
        run_selective_tests.subprocess,
        "run",
        _fake_pytest({"tests/a_test.py": 1, "tests/populace_fixture.py": 5}),
    )
    assert runner.run_tests({"tests/a_test.py", "tests/populace_fixture.py"}) == 1
