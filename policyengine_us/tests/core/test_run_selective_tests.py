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
