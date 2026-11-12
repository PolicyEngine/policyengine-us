"""Check categorical eligibility across generated sibling configurations.

Each draw runs independent SPM units together, reusing one read-only system.
We vary siblings, income tiers, enrollment, K-12 attendance and receipt months.
The paired units hold their poverty ratios fixed when a child joins them.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2025
MONTHS = tuple(f"{YEAR}-{month:02d}" for month in range(1, 13))
CHILD_CATEGORIES = (
    "is_enrolled_in_head_start",
    "is_in_foster_care",
    "is_homeless_child",
    "is_runaway_child",
    "is_migratory_child",
)
HOUSEHOLD_CATEGORIES = ("snap", "receives_snap", "tanf", "receives_tanf", "fdpir")
INCOME_TIERS = ((1.0, "FREE"), (1.5, "REDUCED"), (3.0, "PAID"))
# USDA's SY 2024-25 rates apply on January 1, 2025. Lunch uses the
# under-60-percent rate; breakfast uses the non-severe-need rate.
# https://www.govinfo.gov/content/pkg/FR-2024-07-10/pdf/2024-15175.pdf#page=4
BREAKFAST_RATES = {"FREE": 2.37, "REDUCED": 2.07, "PAID": 0.39}
LUNCH_RATES = {"FREE": 4.43, "REDUCED": 4.03, "PAID": 0.42}
SCHOOL_DAYS = 180


@pytest.fixture(scope="module")
def school_meal_system():
    return Simulation.default_tax_benefit_system_instance


@st.composite
def units(draw):
    ratio, tier = draw(st.sampled_from(INCOME_TIERS))
    return {
        "ages": draw(st.lists(st.integers(6, 17), min_size=1, max_size=3)),
        "ratio": ratio,
        "tier": tier,
        "month": draw(st.sampled_from(MONTHS)),
        "amount": draw(st.integers(1, 5_000)),
        "added_in_k12": draw(st.booleans()),
    }


def _person(age, in_k12):
    return {
        "age": {YEAR: age},
        "is_in_k12_school": {YEAR: in_k12},
        "is_head_start_eligible": {YEAR: False},
        "was_in_foster_care": {YEAR: False},
        **{
            name: {YEAR: False}
            for name in CHILD_CATEGORIES
            if name != "is_in_foster_care"
        },
        "is_in_foster_care": dict.fromkeys(MONTHS, False),
    }


def _situation(drawn_units):
    people = {}
    groups = {"spm_units": {}, "tax_units": {}, "families": {}, "households": {}}
    records = []
    for unit_number, unit in enumerate(drawn_units):
        variants = (
            "base",
            "added",
            *CHILD_CATEGORIES,
            *HOUSEHOLD_CATEGORIES,
            "is_head_start_eligible",
            "was_in_foster_care",
        )
        for variant in variants:
            prefix = f"unit_{unit_number}_{variant}"
            parent = f"{prefix}_parent"
            people[parent] = _person(35, False)
            members = [parent]
            siblings = []
            for index, age in enumerate(unit["ages"]):
                child = f"{prefix}_sibling_{index}"
                people[child] = _person(age, True)
                members.append(child)
                siblings.append(child)
            added = None
            if variant != "base":
                added = f"{prefix}_added"
                people[added] = _person(5, unit["added_in_k12"])
                members.append(added)
                if variant in CHILD_CATEGORIES or variant in (
                    "is_head_start_eligible",
                    "was_in_foster_care",
                ):
                    period = unit["month"] if variant == "is_in_foster_care" else YEAR
                    people[added][variant][period] = True
            spm_unit = {
                "members": members,
                "school_meal_fpg_ratio": {YEAR: unit["ratio"]},
                "snap": dict.fromkeys(MONTHS, 0),
                "tanf": {YEAR: 0},
                "fdpir": {YEAR: 0},
                "receives_snap": dict.fromkeys(MONTHS, False),
                "receives_tanf": dict.fromkeys(MONTHS, False),
            }
            if variant in HOUSEHOLD_CATEGORIES:
                period = YEAR if variant in ("tanf", "fdpir") else unit["month"]
                value = True if variant.startswith("receives_") else unit["amount"]
                spm_unit[variant][period] = value
            groups["spm_units"][prefix] = spm_unit
            groups["tax_units"][prefix] = {"members": members}
            groups["families"][prefix] = {"members": members}
            groups["households"][prefix] = {
                "members": members,
                "state_code": {YEAR: "AL"},
                "is_homeless": {YEAR: False},
            }
            records.append(
                {
                    "unit": unit,
                    "number": unit_number,
                    "variant": variant,
                    "members": members,
                    "siblings": siblings,
                    "added": added,
                }
            )
    return {"people": people, **groups}, records


def _check(drawn_units, system):
    situation, records = _situation(drawn_units)
    simulation = Simulation(situation=situation, tax_benefit_system=system)
    person_index = {name: index for index, name in enumerate(situation["people"])}
    categorical = np.asarray(
        simulation.calculate("is_school_meal_categorically_eligible", YEAR),
        dtype=bool,
    )
    household_categorical = np.asarray(
        simulation.calculate("meets_school_meal_categorical_eligibility", YEAR),
        dtype=bool,
    )
    tiers = {
        meal: simulation.calculate(
            f"school_meal_child_{meal}_tier", YEAR
        ).decode_to_str()
        for meal in ("breakfast", "lunch")
    }
    values = {
        name: np.asarray(simulation.calculate(name, YEAR), dtype=float)
        for name in (
            "school_meal_daily_subsidy",
            "school_meal_net_subsidy",
            "free_school_meals",
            "reduced_price_school_meals",
        )
    }
    sibling_results = {}
    for index, record in enumerate(records):
        unit = record["unit"]
        variant = record["variant"]
        household = variant in HOUSEHOLD_CATEGORIES
        assert household_categorical[index] == household
        daily_total = 0
        net = free = reduced = 0
        school_children = 0
        for name in record["members"]:
            person = person_index[name]
            own_category = name == record["added"] and variant in CHILD_CATEGORIES
            assert categorical[person] == (household or own_category)
            expected_tier = "FREE" if household or own_category else unit["tier"]
            for meal in tiers:
                assert tiers[meal][person] == expected_tier
            if not situation["people"][name]["is_in_k12_school"][YEAR]:
                continue
            school_children += 1
            daily = BREAKFAST_RATES[expected_tier] + LUNCH_RATES[expected_tier]
            daily_total += daily
            # Subtract the paid reimbursement once per child per meal.
            annual = (daily - 0.39 - 0.42) * SCHOOL_DAYS
            net += annual
            free += annual if expected_tier == "FREE" else 0
            reduced += annual if expected_tier == "REDUCED" else 0
        expected = {
            "school_meal_daily_subsidy": daily_total / school_children,
            "school_meal_net_subsidy": net,
            "free_school_meals": free,
            "reduced_price_school_meals": reduced,
        }
        for name, amount in expected.items():
            np.testing.assert_allclose(
                values[name][index], amount, atol=0.01, rtol=0, err_msg=variant
            )
        siblings = [person_index[name] for name in record["siblings"]]
        sibling_results[record["number"], variant] = (
            categorical[siblings],
            tiers["breakfast"][siblings],
            tiers["lunch"][siblings],
        )
    for unit_number in range(len(drawn_units)):
        base = sibling_results[unit_number, "base"]
        for variant in ("added", *CHILD_CATEGORIES):
            for before, after in zip(base, sibling_results[unit_number, variant]):
                np.testing.assert_array_equal(before, after)


@settings(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(drawn_units=st.lists(units(), min_size=1, max_size=3))
def test_school_meal_categorical_eligibility_invariants(
    school_meal_system, drawn_units
):
    _check(drawn_units, school_meal_system)
