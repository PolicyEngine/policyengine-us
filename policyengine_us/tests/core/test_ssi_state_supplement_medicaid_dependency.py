import numpy as np
import pytest

from policyengine_us import Simulation

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")
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


def test_co_oap_medicaid_branch_keeps_reported_coverage():
    """Reported Medicaid coverage holds inside the branch. Two OAP couples and
    an unrelated adult with a $14,000/year pension share one SNAP unit. Spouse
    A reports Medicaid coverage, so A's client gets the full 1,032/month.
    Spouse B, 40, earns $5,000/year as a SNAP workfare participant. With A's
    income exempt the unit gets no SNAP, so B has no route to Medicaid and
    B's earnings are deemed: (5,000 / 12 - 65) / 2 = 175.83/month, a grant
    of 856.17 paid as 856 (3.581(E)), or 10,272/year."""
    year = 2027
    people = {
        "client_a": {"age": {year: 62}},
        "spouse_a": {
            "age": {year: 40},
            "employment_income": {year: 5_000},
            "is_snap_workfare_participant": {year: True},
            "receives_medicaid": {year: True},
            "takes_up_medicaid_if_eligible": {year: False},
        },
        "client_b": {"age": {year: 62}},
        "spouse_b": {
            "age": {year: 40},
            "employment_income": {year: 5_000},
            "is_snap_workfare_participant": {year: True},
        },
        "adult": {
            "age": {year: 40},
            "pension_income": {year: 14_000},
            "is_snap_workfare_participant": {year: True},
        },
    }
    units = {
        "a": {"members": ["client_a", "spouse_a"]},
        "b": {"members": ["client_b", "spouse_b"]},
        "adult": {"members": ["adult"]},
    }
    everyone = {"members": list(people)}
    situation = {
        "people": people,
        **{entity: units for entity in ("tax_units", "marital_units", "families")},
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
    assert results[0]["co_oap"][2] == pytest.approx(10_272)


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


SSP = {"IN": ("in_ssp", "in_ssp_sapn_eligible"), "KS": ("ks_sspp", "ks_sspp_eligible")}
SSP_MEDICAID = "medicaid_enrolled_for_ssi_state_supplement"
PASS_THROUGH = "medicaid_community_engagement_pass_through_eligible"
# Variables a caller may calculate before the SSP's Medicaid enrollment, each
# with the period it is asked for.
CALCULATED_FIRST = {
    "medicaid_enrolled": 2027,
    "is_medicaid_eligible": 2027,
    PASS_THROUGH: "2027-01",
    "snap": "2027-01",
    "in_ssp": "2027-01",
    "ks_sspp": "2027-01",
}


def supplied_situation(state, supplied, year=2027):
    """``situation`` with one value on the SNAP-SSP-Medicaid cycle supplied.

    Supplying SNAP or the pass-through means calculating medicaid_enrolled no
    longer runs the SSP on the way, so medicaid_enrolled can be stored before
    the SSP's Medicaid enrollment is first asked for.
    """
    data = situation(year, state)
    if supplied == "snap":
        data["spm_units"]["recipient"]["snap"] = {year: 0}
        data["spm_units"]["adult"]["snap"] = {year: 1_200}
    elif supplied == "pass_through":
        data["people"]["adult"][PASS_THROUGH] = {f"{year}-01": True}
    elif supplied == "medicaid_enrolled":
        data["people"]["recipient"]["medicaid_enrolled"] = {year: True}
        data["people"]["adult"]["medicaid_enrolled"] = {year: True}
    return data


@hypothesis.settings(max_examples=6, deadline=None, derandomize=True)
# The reproducing case: with SNAP supplied, the SNAP pass-through adult's SSP
# enrollment was False asked alone, but True once medicaid_enrolled, which
# keeps the pass-through, had been calculated.
@hypothesis.example(state="IN", supplied="snap", first=["medicaid_enrolled"])
@hypothesis.given(
    state=st.sampled_from(["IN", "KS"]),
    supplied=st.sampled_from([None, "snap", "pass_through", "medicaid_enrolled"]),
    first=st.lists(st.sampled_from(list(CALCULATED_FIRST)), unique=True, max_size=4),
)
def test_ssp_medicaid_enrollment_does_not_depend_on_calculation_order(
    state, supplied, first
):
    benefit, eligibility = SSP[state]
    fresh = Simulation(situation=supplied_situation(state, supplied))
    simulation = Simulation(situation=supplied_situation(state, supplied))
    for name in first:
        simulation.calculate(name, CALCULATED_FIRST[name])
    for name, year in ((SSP_MEDICAID, 2027), (eligibility, "2027-01"), (benefit, 2027)):
        np.testing.assert_array_equal(
            simulation.calculate(name, year), fresh.calculate(name, year)
        )


@pytest.mark.parametrize("route", ["snap", "tanf"])
@pytest.mark.parametrize("first", [(), ("medicaid_enrolled",)])
def test_pass_through_adult_drops_the_exclusion_in_either_order(route, first):
    """The adult is enrolled in Medicaid only through the SNAP or TANF
    exclusion from the community engagement requirement. SNAP is supplied, so
    medicaid_enrolled can be stored first. The SSP's enrollment drops the
    exclusion whether or not medicaid_enrolled was calculated first."""
    data = supplied_situation("IN", "snap")
    if route == "tanf":
        data["people"]["adult"].pop("is_snap_workfare_participant")
        data["spm_units"]["adult"]["snap"] = {2027: 0}
        data["spm_units"]["adult"]["receives_tanf"] = {2027: True}
        data["spm_units"]["adult"]["meets_tanf_work_requirements"] = {2027: True}
    simulation = Simulation(situation=data)
    for name in first:
        simulation.calculate(name, CALCULATED_FIRST[name])
    assert simulation.calculate(SSP_MEDICAID, 2027).tolist() == [True, False]
    assert simulation.calculate("medicaid_enrolled", 2027).tolist() == [True, True]


@pytest.mark.parametrize("first", [(), ("medicaid_enrolled",)])
def test_ssi_recipient_in_the_adult_group_gets_the_same_sapn_in_either_order(first):
    """A reform that ends Indiana's Medicaid coverage of SSI recipients puts
    this 40-year-old, institutionalized SSI recipient with no disability
    finding in the adult group, where the community engagement requirement
    applies; ``is_ssi_recipient_for_medicaid: False`` does the same here. The
    recipient is exempt only through the supplied SNAP pass-through, which
    the SSP's enrollment drops. SAPN was $22 when medicaid_enrolled had been
    calculated first and $0 otherwise; it is now $0 in either order."""
    year = 2027
    people = {
        "recipient": {
            "age": {year: 40},
            "receives_ssi": {year: True},
            "is_ssi_recipient_for_medicaid": {year: False},
            "ssi_lives_in_medical_treatment_facility": {year: True},
            "ssi_medicaid_pays_majority_of_care": {year: True},
            PASS_THROUGH: {f"{year}-01": True},
        }
    }
    unit = {"unit": {"members": ["recipient"]}}
    simulation = Simulation(
        situation={
            "people": people,
            **{e: unit for e in ("tax_units", "spm_units", "families")},
            "households": {
                "unit": {"members": ["recipient"], "state_code": {year: "IN"}}
            },
        }
    )
    for name in first:
        simulation.calculate(name, CALCULATED_FIRST[name])
    # Ask for the SSP before medicaid_enrolled, so that with nothing
    # calculated first this is the order in which the SSP comes first.
    assert simulation.calculate(SSP_MEDICAID, year).tolist() == [False]
    assert simulation.calculate("in_ssp_sapn_eligible", f"{year}-01").tolist() == [
        False
    ]
    assert simulation.calculate("in_ssp", year).tolist() == [0]
    assert simulation.calculate("medicaid_category", year).decode_to_str().tolist() == [
        "ADULT"
    ]
    assert simulation.calculate("medicaid_enrolled", year).tolist() == [True]


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
