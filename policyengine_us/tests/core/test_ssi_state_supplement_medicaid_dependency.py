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


def co_oap_couple(year, snap=None):
    """An Old Age Pension client whose spouse is a SNAP workfare participant."""
    people = {
        "client": {"age": {year: 62}},
        "spouse": {
            "age": {year: 40},
            "employment_income": {year: 5_000},
            "is_snap_workfare_participant": {year: True},
        },
    }
    unit = {"unit": {"members": list(people)}}
    spm_units = {"unit": {"members": list(people)}}
    if snap is not None:
        spm_units["unit"]["snap"] = {year: snap}
    return {
        "people": people,
        **{entity: unit for entity in ("tax_units", "marital_units", "families")},
        "spm_units": spm_units,
        "households": {"unit": {"members": list(people), "state_code": {year: "CO"}}},
    }


@pytest.mark.parametrize("year", [2027, 2030, 2035])
@pytest.mark.parametrize("snap", [None, 12])
def test_co_oap_snap_medicaid_calculation_order(year, snap):
    """Colorado OAP reads the spouse's Medicaid enrollment to decide whether the
    spouse's income is deemed (9 CCR 2503-5 3.534(C)), and SNAP counts OAP as
    income. The spouse is enrolled through SNAP's pass-through from the
    community engagement requirement, with SNAP computed or supplied, and
    earns $5,000/year, well within the OAP limit, so nothing is deemed and the
    client gets the full 1,032/month in either order. YAML cannot express
    repeated calculations in different orders."""
    variables = ("co_oap", "snap", "medicaid_enrolled")
    results = []
    for order in (variables, variables[::-1]):
        simulation = Simulation(situation=co_oap_couple(year, snap))
        results.append({name: simulation.calculate(name, year) for name in order})
        assert not any("_medicaid_" in name for name in simulation.branches)
    for name in variables:
        np.testing.assert_array_equal(results[0][name], results[1][name])
    assert results[0]["medicaid_enrolled"].tolist() == [True, True]
    assert results[0]["co_oap"][0] == pytest.approx(12_384)
    assert results[0]["snap"][0] > 0


def test_co_oap_medicaid_without_a_consistent_outcome():
    """A household with no self-consistent outcome resolves the same way in
    either order. The client's spouse, 40, earns $5,000/year and is a SNAP
    workfare participant; an unrelated adult in the same SNAP unit has a
    $31,250/year pension. With the spouse's income deemed, OAP is lower and
    the unit gets SNAP, which enrolls the spouse in Medicaid through the
    pass-through; with the spouse exempt, OAP is higher and the unit gets no
    SNAP. co_oap_medicaid_enrolled decides enrollment on the SNAP received
    while the spouse's income is still deemed, so the spouse is exempt and
    the client gets the full 1,032/month."""
    year = 2027
    people = {
        "client": {"age": {year: 62}},
        "spouse": {
            "age": {year: 40},
            "employment_income": {year: 5_000},
            "is_snap_workfare_participant": {year: True},
        },
        "adult": {
            "age": {year: 40},
            "pension_income": {year: 31_250},
            "is_snap_workfare_participant": {year: True},
        },
    }
    couple = {"members": ["client", "spouse"]}
    single = {"members": ["adult"]}
    everyone = {"members": list(people)}
    situation = {
        "people": people,
        **{
            entity: {"couple": couple, "single": single}
            for entity in ("tax_units", "marital_units", "families")
        },
        "spm_units": {"unit": everyone},
        "households": {"unit": {**everyone, "state_code": {year: "CO"}}},
    }
    variables = ("co_oap", "snap", "medicaid_enrolled")
    results = []
    for order in (variables, variables[::-1]):
        simulation = Simulation(situation=situation)
        results.append({name: simulation.calculate(name, year) for name in order})
    for name in variables:
        np.testing.assert_array_equal(results[0][name], results[1][name])
    assert results[0]["co_oap"][0] == pytest.approx(12_384)


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
    assert poor.dtype == np.dtype(bool)
    assert poor.size == len(groups)
    assert np.isfinite(simulation.calculate("spm_unit_benefits", year)).all()
