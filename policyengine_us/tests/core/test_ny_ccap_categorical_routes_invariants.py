"""Check New York CCAP defaults, categorical routes and family shares."""

from copy import deepcopy

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system as tax_benefit_system


YEARS = [2024, 2025, 2026]
TITLE_XX_CHILD_AGES = (0, 4, 12, 13, 14, 15, 17)
TOLERANCE = 0.001
SPM_MONTH_INPUTS = (
    "ny_safety_net_assistance_received",
    "ny_veteran_assistance_received",
    "ny_ccap_required_activity",
    "ny_ccap_child_only_unit",
)
PERSON_MONTH_INPUTS = (
    "ny_ccap_receives_preventive_services",
    "ny_ccap_title_xx_preventive_services_approved",
)
NEW_INPUTS = SPM_MONTH_INPUTS + PERSON_MONTH_INPUTS
OUTPUTS = (
    "ny_ccap_activity_eligible",
    "ny_ccap_protective_services_case",
    "ny_ccap_family_share_exempt",
    "ny_ccap_family_share",
    "ny_ccap",
)
PROPERTY_SETTINGS = settings(
    max_examples=12,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@pytest.fixture(scope="module")
def system():
    return tax_benefit_system


@st.composite
def families(draw):
    return {
        "caretakers": draw(st.tuples(st.booleans(), st.booleans())),
        "hours": draw(
            st.tuples(
                st.sampled_from([0, 1, 20, 40]),
                st.sampled_from([0, 1, 20, 40]),
            )
        ),
        "students": draw(st.tuples(st.booleans(), st.booleans())),
        "tanf": draw(st.booleans()),
        "fallback": draw(st.booleans()),
        "homeless": draw(st.booleans()),
        "protective": draw(st.tuples(st.booleans(), st.booleans(), st.booleans())),
        "foster": draw(st.booleans()),
        "age_eligible": draw(st.booleans()),
        "asset_eligible": draw(st.booleans()),
        "immigration_eligible": draw(st.booleans()),
        "income_eligible": draw(st.booleans()),
        "income": draw(st.integers(0, 20_000)),
        "fpg": draw(st.integers(0, 8_000)),
        "expenses": draw(st.integers(0, 6_000)),
        "market_rate": draw(st.integers(0, 6_000)),
        "in_care": draw(st.booleans()),
        "new_inputs": {name: draw(st.booleans()) for name in NEW_INPUTS},
    }


def _situation(cases, year):
    month = f"{year}-10"
    situation = {
        "people": {},
        "tax_units": {},
        "spm_units": {},
        "families": {},
        "marital_units": {},
        "households": {},
    }
    for index, (family, flags) in enumerate(cases):
        members = [f"adult_a_{index}", f"adult_b_{index}", f"child_{index}"]
        for person_index, name in enumerate(members):
            child = person_index == 2
            person = {
                "age": {
                    year: family.get("child_age", 4) if child else 35 + person_index
                },
                "is_tax_unit_head_or_spouse": {
                    year: False if child else family["caretakers"][person_index]
                },
                "weekly_hours_worked_before_lsr": {
                    year: 0 if child else family["hours"][person_index]
                },
                "is_full_time_student": {
                    year: False if child else family["students"][person_index]
                },
                "receives_or_needs_protective_services": {
                    year: family["protective"][person_index]
                },
                "is_in_foster_care": {month: child and family["foster"]},
                "ny_ccap_age_eligible": {year: child and family["age_eligible"]},
                "is_ccdf_immigration_eligible_child": {
                    year: child and family["immigration_eligible"]
                },
                "childcare_hours_per_day": {
                    year: 8 if child and family["in_care"] else 0
                },
                "ny_ccap_market_rate": {month: family["market_rate"] if child else 0},
            }
            for variable in PERSON_MONTH_INPUTS:
                if flags is not None:
                    person[variable] = {month: child and flags[variable]}
            situation["people"][name] = person
        unit = {
            "members": members,
            "is_tanf_enrolled": {month: family["tanf"]},
            "meets_ccdf_activity_test": {year: family["fallback"]},
            "ny_ccap_countable_income": {year: 12 * family["income"]},
            "spm_unit_fpg": {year: 12 * family["fpg"]},
            "spm_unit_pre_subsidy_childcare_expenses": {year: 12 * family["expenses"]},
            "ny_ccap_income_eligible": {month: family["income_eligible"]},
            "is_ccdf_asset_eligible": {year: family["asset_eligible"]},
        }
        if flags is not None:
            for variable in SPM_MONTH_INPUTS:
                unit[variable] = {month: flags[variable]}
        situation["spm_units"][f"unit_{index}"] = unit
        for group in ("tax_units", "families"):
            situation[group][f"{group}_{index}"] = {"members": members}
        situation["marital_units"][f"adults_{index}"] = {"members": members[:2]}
        situation["marital_units"][f"child_{index}"] = {"members": members[2:]}
        situation["households"][f"household_{index}"] = {
            "members": members,
            "state_code": {year: "NY"},
            "is_homeless": {year: family["homeless"]},
        }
    return situation


def _calculate(system, cases, year):
    month = f"{year}-10"
    simulation = Simulation(
        tax_benefit_system=system,
        situation=_situation(cases, year),
    )
    outputs = {
        name: np.asarray(
            simulation.calculate(
                name, year if name == "ny_ccap_protective_services_case" else month
            )
        )
        for name in OUTPUTS
    }
    outputs["eligible_people"] = np.asarray(
        simulation.calculate("ny_ccap_eligible_child", month)
    ).reshape(-1, 3)
    outputs["ny_ccap_eligible_child"] = outputs["eligible_people"][:, 2]
    for name in (
        "ny_ccap_countable_income",
        "spm_unit_fpg",
        "spm_unit_pre_subsidy_childcare_expenses",
    ):
        outputs[name] = np.asarray(simulation.calculate(name, month))
    for name, values in outputs.items():
        assert np.isfinite(values).all(), f"{name} contains a nonfinite result"
    return outputs


def _work_eligible(family):
    return any(family["caretakers"]) and all(
        not caretaker or hours > 0 or student
        for caretaker, hours, student in zip(
            family["caretakers"], family["hours"], family["students"]
        )
    )


def _eligible_child(family, activity):
    protective = any(family["protective"])
    return (
        family["age_eligible"]
        and family["asset_eligible"]
        and family["immigration_eligible"]
        and (activity or protective or family["foster"] or family["homeless"])
        and (family["income_eligible"] or protective or family["foster"])
    )


@PROPERTY_SETTINGS
@given(st.sampled_from(YEARS), st.lists(families(), min_size=2, max_size=8))
def test_defaults_preserve_main_except_public_assistance_activity(system, year, units):
    defaults = dict.fromkeys(NEW_INPUTS, False)
    cases = [(unit, flags) for unit in units for flags in (None, defaults)]
    outputs = _calculate(system, cases, year)
    for name in OUTPUTS + ("ny_ccap_eligible_child",):
        np.testing.assert_allclose(
            outputs[name][0::2], outputs[name][1::2], atol=TOLERANCE, rtol=0
        )

    p = system.parameters(f"{year}-10").gov.states.ny.ocfs.ccap
    for index, unit in enumerate(units):
        actual_index = 2 * index
        work = _work_eligible(unit)
        main_activity = work or unit["tanf"] or unit["fallback"]
        activity = work or unit["fallback"]
        protective = any(unit["protective"])
        exempt = unit["tanf"] or unit["homeless"] or unit["foster"] or protective
        income = outputs["ny_ccap_countable_income"][actual_index]
        fpg = outputs["spm_unit_fpg"][actual_index]
        expenses = outputs["spm_unit_pre_subsidy_childcare_expenses"][actual_index]
        family_share = (
            max(
                (income - fpg) * p.family_share_rate,
                p.minimum_weekly_family_share * 52 / 12,
            )
            if income > fpg and not exempt
            else 0
        )
        eligible = _eligible_child(unit, activity)
        main_eligible = _eligible_child(unit, main_activity)
        reimbursable = min(expenses, unit["market_rate"]) if unit["in_care"] else 0
        benefit = max(reimbursable * eligible - family_share, 0)
        main_benefit = max(reimbursable * main_eligible - family_share, 0)
        assert outputs["ny_ccap_activity_eligible"][actual_index] == activity
        assert outputs["ny_ccap_protective_services_case"][actual_index] == protective
        assert outputs["ny_ccap_family_share_exempt"][actual_index] == exempt
        assert outputs["ny_ccap_family_share"][actual_index] == pytest.approx(
            family_share, abs=TOLERANCE
        )
        assert outputs["ny_ccap_eligible_child"][actual_index] == eligible
        assert outputs["ny_ccap"][actual_index] == pytest.approx(benefit, abs=TOLERANCE)
        intended_activity_loss = unit["tanf"] and not work and not unit["fallback"]
        if not intended_activity_loss:
            assert eligible == main_eligible
            assert benefit == pytest.approx(main_benefit, abs=TOLERANCE)
        else:
            assert eligible <= main_eligible
            assert benefit <= main_benefit + TOLERANCE


@PROPERTY_SETTINGS
@given(st.sampled_from(YEARS), st.lists(families(), min_size=2, max_size=8))
def test_categorical_inputs_never_raise_share_or_lower_ccap(system, year, units):
    cases = []
    for unit in units:
        for variable in NEW_INPUTS:
            for value in (False, True):
                cases.append((unit, {**unit["new_inputs"], variable: value}))
    outputs = _calculate(system, cases, year)
    share = outputs["ny_ccap_family_share"]
    benefit = outputs["ny_ccap"]
    assert (share[1::2] <= share[0::2] + TOLERANCE).all()
    assert (benefit[1::2] + TOLERANCE >= benefit[0::2]).all()
    exempt = outputs["ny_ccap_family_share_exempt"].astype(bool)
    np.testing.assert_array_equal(share[exempt], 0)
    assert (share >= 0).all()
    assert (benefit >= 0).all()


@PROPERTY_SETTINGS
@given(st.sampled_from(YEARS), families())
def test_public_assistance_needs_work_or_required_activity(system, year, unit):
    idle = deepcopy(unit)
    idle.update(
        caretakers=(True, True),
        hours=(0, 0),
        students=(False, False),
        fallback=False,
        homeless=False,
        protective=(False, False, False),
        foster=False,
        age_eligible=True,
        asset_eligible=True,
        immigration_eligible=True,
        income_eligible=True,
    )
    cases = []
    expected = []
    for source in (None, "tanf", "safety_net", "veteran"):
        for required in (False, True):
            family = {**idle, "tanf": source == "tanf"}
            flags = dict.fromkeys(NEW_INPUTS, False)
            flags["ny_safety_net_assistance_received"] = source == "safety_net"
            flags["ny_veteran_assistance_received"] = source == "veteran"
            flags["ny_ccap_required_activity"] = required
            cases.append((family, flags))
            expected.append(source is not None and required)
    outputs = _calculate(system, cases, year)
    np.testing.assert_array_equal(outputs["ny_ccap_activity_eligible"], expected)
    np.testing.assert_array_equal(outputs["ny_ccap_eligible_child"], expected)
    np.testing.assert_array_equal(outputs["ny_ccap"][0::2], 0)


@PROPERTY_SETTINGS
@given(st.sampled_from(YEARS), families())
def test_title_xx_approval_serves_only_the_preventive_child(system, year, unit):
    # 18 NYCRR 415.1(b) and 415.2(d)(4)(ii): the Title XX route keeps the age
    # test. A child under 13 passes it, and so does an older child under the
    # special-needs or court-supervision extensions, drawn here through
    # unit["age_eligible"]. A 13-year-old may finish the school year in which
    # the child turned 13, which ends before the child turns 14.
    flag_pairs = ((False, False), (True, False), (False, True), (True, True))
    cases = []
    expected_eligible = []
    expected_exempt = []
    for child_age in TITLE_XX_CHILD_AGES:
        age_eligible = child_age < 13 or unit["age_eligible"]
        blocked = deepcopy(unit)
        blocked.update(
            child_age=child_age,
            hours=(0, 0),
            students=(False, False),
            tanf=False,
            fallback=False,
            homeless=False,
            protective=(False, False, False),
            foster=False,
            age_eligible=age_eligible,
            asset_eligible=False,
            immigration_eligible=False,
            income_eligible=False,
            in_care=True,
            expenses=max(unit["expenses"], 1),
            market_rate=max(unit["market_rate"], 1),
        )
        title_xx_age_eligible = age_eligible or child_age == 13
        for preventive, approved in flag_pairs:
            flags = dict.fromkeys(NEW_INPUTS, False)
            flags["ny_ccap_receives_preventive_services"] = preventive
            flags["ny_ccap_title_xx_preventive_services_approved"] = approved
            cases.append((blocked, flags))
            expected_eligible.append(preventive and approved and title_xx_age_eligible)
            expected_exempt.append(preventive)
    outputs = _calculate(system, cases, year)
    np.testing.assert_array_equal(outputs["ny_ccap_eligible_child"], expected_eligible)
    assert not outputs["eligible_people"][:, :2].any()
    np.testing.assert_array_equal(
        outputs["ny_ccap_family_share_exempt"], expected_exempt
    )
    eligible = np.array(expected_eligible)
    np.testing.assert_array_equal(outputs["ny_ccap"][~eligible], 0)
    assert (outputs["ny_ccap"][eligible] > 0).all()
