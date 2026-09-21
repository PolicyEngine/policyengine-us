from policyengine_us.system import system


def test_org_input_variables_exist():
    assert "hourly_wage" in system.variables
    assert "is_union_member_or_covered" in system.variables


def test_org_input_variable_types():
    assert system.variables["hourly_wage"].value_type is float
    assert system.variables["is_union_member_or_covered"].value_type is bool
