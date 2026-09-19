import numpy as np
import pytest

from policyengine_us import Simulation


def situation(year):
    people = {
        "recipient": {
            "age": {year: 45},
            "meets_ssi_disability_criteria": {year: True},
            "ssi_lives_in_medical_treatment_facility": {year: True},
            "ssi_medicaid_pays_majority_of_care": {year: True},
        },
        "adult": {
            "age": {year: 40},
            "employment_income": {year: 5_000},
            # Workfare satisfies SNAP's work test without supplying the
            # independent hours/income exemptions in Medicaid's calculation.
            "is_snap_workfare_participant": {year: True},
        },
    }
    return {
        "people": people,
        **{
            entity: {name: {"members": [name]} for name in people}
            for entity in ("tax_units", "spm_units", "families")
        },
        "households": {
            name: {"members": [name], "state_code": {year: "IN"}} for name in people
        },
    }


@pytest.mark.parametrize("year", [2027, 2030, 2035])
def test_ssp_snap_medicaid_calculation_order(year):
    """YAML cannot express repeated calculations in different orders."""
    variables = ("in_ssp", "snap", "medicaid_enrolled")
    results = []
    for order in (variables, variables[::-1]):
        simulation = Simulation(situation=situation(year))
        results.append({name: simulation.calculate(name, year) for name in order})
        # The temporary SSP calculation must not retain a population-sized branch.
        assert not any("in_ssp_medicaid" in name for name in simulation.branches)
    for name in variables:
        np.testing.assert_array_equal(results[0][name], results[1][name])
    assert results[0]["in_ssp"][0] > 0
    assert results[0]["snap"][1] > 0
    assert results[0]["medicaid_enrolled"].tolist() == [True, True]


@pytest.mark.parametrize(
    "variable",
    ["medicaid_enrolled", "is_medicaid_eligible", "takes_up_medicaid_if_eligible"],
)
def test_ssp_preserves_medicaid_inputs_set_after_initialization(variable):
    """Simulation.set_input overrides must survive the private SSP calculation."""
    simulation = Simulation(situation=situation(2030))
    simulation.set_input(variable, 2030, [False, True])
    assert simulation.calculate("in_ssp_sapn_eligible", "2030-01").tolist() == [
        False,
        False,
    ]
    assert simulation.calculate(variable, 2030).tolist() == [False, True]
