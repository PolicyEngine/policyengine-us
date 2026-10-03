import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.variables.household.demographic.geographic.state_code import (
    StateCode,
)


def situation(year, state="IN"):
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
            name: {"members": [name], "state_code": {year: state}} for name in people
        },
    }


@pytest.mark.parametrize("year", [2027, 2030, 2035])
@pytest.mark.parametrize("state,benefit", [("IN", "in_ssp"), ("KS", "ks_sspp")])
def test_ssp_snap_medicaid_calculation_order(year, state, benefit):
    """YAML cannot express repeated calculations in different orders."""
    variables = (benefit, "snap", "medicaid_enrolled")
    results = []
    for order in (variables, variables[::-1]):
        simulation = Simulation(situation=situation(year, state))
        results.append({name: simulation.calculate(name, year) for name in order})
        # The temporary SSP calculation must not retain a population-sized branch.
        assert not any(
            "ssi_state_supplement_medicaid" in name for name in simulation.branches
        )
    for name in variables:
        np.testing.assert_array_equal(results[0][name], results[1][name])
    assert results[0][benefit][0] > 0
    assert results[0]["snap"][1] > 0
    # Kansas does not cover this childless adult through Medicaid expansion;
    # SNAP pass-through does not replace Medicaid's category requirement.
    assert results[0]["medicaid_enrolled"].tolist() == [True, state == "IN"]


@pytest.mark.parametrize(
    "variable",
    ["medicaid_enrolled", "is_medicaid_eligible", "takes_up_medicaid_if_eligible"],
)
@pytest.mark.parametrize(
    "state,eligibility", [("IN", "in_ssp_sapn_eligible"), ("KS", "ks_sspp_eligible")]
)
def test_ssp_preserves_medicaid_inputs_set_after_initialization(
    variable, state, eligibility
):
    """Simulation.set_input overrides must survive the private SSP calculation."""
    simulation = Simulation(situation=situation(2030, state))
    simulation.set_input(variable, 2030, [False, True])
    assert simulation.calculate(eligibility, "2030-01").tolist() == [
        False,
        False,
    ]
    assert simulation.calculate(variable, 2030).tolist() == [False, True]


@pytest.mark.parametrize("year", [2027, 2030, 2035])
def test_future_poverty_in_all_states(year):
    """Exercise state benefit dependencies together, as a national dataset does."""
    people, households, groups = {}, {}, {}
    territories = {"GU", "MP", "PW", "PR", "VI", "AA", "AE", "AP"}
    for state in StateCode:
        if state.name in territories:
            continue
        for role, data in situation(year)["people"].items():
            name = f"{state.name}_{role}"
            people[name] = data
            groups[name] = {"members": [name]}
            households[name] = {
                "members": [name],
                "state_code": {year: state.name},
            }
        child = f"{state.name}_child"
        adult = f"{state.name}_adult"
        people[child] = {
            "age": {year: 8},
            "is_tax_unit_dependent": {year: True},
        }
        groups[adult]["members"].append(child)
        households[adult]["members"].append(child)
    simulation = Simulation(
        # These synthetic state fixtures do not choose a county. Exercise the
        # real poverty calculation using its explicit national threshold mode.
        spm={"geography_kind": "national"},
        situation={
            "people": people,
            "households": households,
            **{entity: groups for entity in ("tax_units", "spm_units", "families")},
        },
    )
    poor = simulation.calculate("spm_unit_is_in_spm_poverty", year)
    # The canonical indicator is a nullable float now that SPM measurement scope
    # is an explicit source decision: NaN marks a record outside the declared
    # universe. A household situation is wholly in-universe, so every unit here
    # is observed, and none of these states may go missing.
    assert np.issubdtype(poor.dtype, np.floating)
    assert np.isin(poor, [0.0, 1.0]).all()
    assert poor.size == len(groups)
    assert np.isfinite(simulation.calculate("spm_unit_benefits", year)).all()
