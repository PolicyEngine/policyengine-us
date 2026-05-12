import numpy as np

from policyengine_us.variables.gov.fcc.acp import is_acp_eligible as acp_module
from policyengine_us.variables.gov.fcc.ebb import is_ebb_eligible as ebb_module


class _Node:
    def __init__(self, values=None):
        self.values = values or {}

    def __call__(self, variable, period):
        return self.values[variable]


class _Parameters:
    def __init__(self, gov):
        self.gov = gov

    def __call__(self, period):
        return self


def _parameter_tree():
    class Node:
        pass

    gov = Node()
    gov.fcc = Node()
    gov.fcc.acp = Node()
    gov.fcc.acp.categorical_eligibility = ["lifeline", "wic"]
    gov.fcc.acp.fpg_limit = 2
    gov.fcc.ebb = Node()
    gov.fcc.ebb.categorical_eligibility = ["pell_grant"]
    gov.fcc.ebb.prior_enrollment_required = True
    gov.fcc.lifeline = Node()
    gov.fcc.lifeline.categorical_eligibility = ["medicaid"]
    gov.fcc.lifeline.tribal_categorical_eligibility = ["fdpir"]
    return _Parameters(gov)


def test_acp_lifeline_categorical_eligibility_is_vectorized(monkeypatch):
    spm_unit = _Node(
        {
            "fcc_fpg_ratio": np.array([2.1, 2.1, 2.1]),
            "ebb": np.array([0, 0, 0]),
        }
    )
    spm_unit.household = _Node(
        {"is_on_tribal_land": np.array([False, True, True])}
    )
    program_values = {
        "lifeline": np.array([0, 0, 0]),
        "wic": np.array([0, 0, 0]),
        "medicaid": np.array([1, 1, 0]),
        "fdpir": np.array([0, 0, 1]),
    }

    def fake_add(entity, period, variables):
        return sum(program_values[variable] for variable in variables)

    monkeypatch.setattr(acp_module, "add", fake_add)

    result = acp_module.is_acp_eligible.formula(spm_unit, "2022", _parameter_tree())

    np.testing.assert_array_equal(result, np.array([True, False, True]))


def test_ebb_categorical_eligibility_is_vectorized(monkeypatch):
    spm_unit = _Node({"enrolled_in_ebb": np.array([True, True])})
    program_values = {"pell_grant": np.array([1, 0])}

    def fake_add(entity, period, variables):
        return sum(program_values[variable] for variable in variables)

    monkeypatch.setattr(ebb_module, "add", fake_add)

    result = ebb_module.is_ebb_eligible.formula(spm_unit, "2022", _parameter_tree())

    np.testing.assert_array_equal(result, np.array([True, False]))
