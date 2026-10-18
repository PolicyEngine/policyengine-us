"""Properties of eligible long-term care premiums on Schedule A.

26 U.S.C. 213(d)(1)(D) counts premiums for a qualified long-term care
insurance contract as medical care up to the 213(d)(10) limit for the insured
person's age at the end of the year. 162(l)(2)(C) lets the same eligible
premiums into the self-employed health insurance deduction, and 162(l)(3)
keeps the part deducted there off Schedule A.

The limits below are typed from the Rev. Proc. tables, independently of the
parameter file, so the first test is a differential check of the parameter
against the published amounts. The other properties run generated tax units
(single, joint, with dependents; self-employed or not; the deduction derived
from self-employment income or supplied for the return) through one
vectorized simulation per example. Every unit appears twice: as drawn, and
with each person's long-term care premiums raised. Medicare enrollment is off,
so a person's medical insurance premiums are exactly their direct input. For
every tax unit:

1. Eligible premiums equal min(premiums, published limit for the age), with
   ages at each band edge; they are never negative or above the premiums.
2. The self-employed exclusion takes medical insurance premiums first:
   medical part = min(filers' medical premiums, deduction); long-term care
   part = min(filers' eligible premiums, deduction - medical part); together
   they equal min(filers' medical + eligible premiums, deduction), and the
   applied exclusion of a computed subtotal is their sum.
3. Accounting: the subtotal is members' medical premiums - medical part +
   members' eligible premiums - long-term care part + other expenses, and the
   long-term care premiums inside it lie between the dependents' eligible
   premiums and all members' eligible premiums.
4. Conservation (derived deduction): every eligible premium is deducted once,
   on Schedule A or as the self-employed deduction, never both.
5. The derived person deduction is min(max(0, earnings), health premiums +
   eligible long-term care premiums) for the self-employed, else 0.
6. Monotonicity: raising long-term care premiums never lowers the subtotal
   and raises it by at most the rise in eligible premiums; for units with no
   deduction it raises it by exactly that amount.
7. A supplied subtotal holds no computed long-term care premiums and no
   applied exclusion.
8. Years after the last published table: every amount is a multiple of $10,
   amounts rise with age, and no amount falls from one year to the next.
"""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

TOLERANCE = 0.01

# Rev. Proc. tables: 40 or less, 41-50, 51-60, 61-70, over 70.
PUBLISHED_LIMITS = {
    2013: (360, 680, 1_360, 3_640, 4_550),  # Rev. Proc. 2012-41
    2014: (370, 700, 1_400, 3_720, 4_660),  # Rev. Proc. 2013-35
    2015: (380, 710, 1_430, 3_800, 4_750),  # Rev. Proc. 2014-61
    2016: (390, 730, 1_460, 3_900, 4_870),  # Rev. Proc. 2015-53
    2017: (410, 770, 1_530, 4_090, 5_110),  # Rev. Proc. 2016-55
    2018: (420, 780, 1_560, 4_160, 5_200),  # Rev. Proc. 2017-58
    2019: (420, 790, 1_580, 4_220, 5_270),  # Rev. Proc. 2018-57
    2020: (430, 810, 1_630, 4_350, 5_430),  # Rev. Proc. 2019-44
    2021: (450, 850, 1_690, 4_520, 5_640),  # Rev. Proc. 2020-45
    2022: (450, 850, 1_690, 4_510, 5_640),  # Rev. Proc. 2021-45
    2023: (480, 890, 1_790, 4_770, 5_960),  # Rev. Proc. 2022-38
    2024: (470, 880, 1_760, 4_710, 5_880),  # Rev. Proc. 2023-34
    2025: (480, 900, 1_800, 4_810, 6_020),  # Rev. Proc. 2024-40
    2026: (500, 930, 1_860, 4_960, 6_200),  # Rev. Proc. 2025-32
}
BAND_TOPS = (40, 50, 60, 70)
LAST_PUBLISHED = max(PUBLISHED_LIMITS)
EDGE_AGES = [0, 18, 39, 40, 41, 50, 51, 60, 61, 70, 71, 95]


def _band(age):
    return sum(age > top for top in BAND_TOPS)


def _published_limit(year, age):
    return PUBLISHED_LIMITS[year][_band(age)]


def _limit_parameter(year):
    return system.parameters(
        f"{year}-01-01"
    ).gov.irs.deductions.itemized.medical.long_term_care_premium_limit


def test_parameter_matches_published_limits():
    for year in PUBLISHED_LIMITS:
        scale = _limit_parameter(year)
        ages = np.array(EDGE_AGES, dtype=float)
        expected = [_published_limit(year, age) for age in EDGE_AGES]
        np.testing.assert_array_equal(scale.calc(ages, right=True), expected)


def test_limits_after_the_last_published_year():
    previous = np.array(PUBLISHED_LIMITS[LAST_PUBLISHED], dtype=float)
    ages = np.array([30, 45, 55, 65, 75], dtype=float)
    for year in range(LAST_PUBLISHED + 1, LAST_PUBLISHED + 10):
        amounts = _limit_parameter(year).calc(ages, right=True)
        assert (amounts % 10 == 0).all(), (year, amounts)
        assert (np.diff(amounts) > 0).all(), (year, amounts)
        assert (amounts >= previous).all(), (year, amounts, previous)
        previous = amounts


premium = st.one_of(st.just(0), st.integers(1, 12_000))
expense = st.one_of(st.just(0), st.integers(1, 15_000))


@st.composite
def people(draw, adult=True):
    self_employed = draw(st.booleans())
    return {
        "age": draw(st.sampled_from(EDGE_AGES[2:] if adult else EDGE_AGES)),
        "self_employed": self_employed,
        "earnings": draw(st.integers(-10_000, 60_000)) if self_employed else 0,
        "health_premiums": draw(expense),
        "long_term_care": draw(premium),
        "long_term_care_rise": draw(st.integers(0, 8_000)),
        "other": draw(expense),
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "joint", "joint_dependents", "hoh"]))
    n_dependents = draw(st.integers(1, 2)) if kind in ("joint_dependents", "hoh") else 0
    return {
        "head": draw(people()),
        "spouse": draw(people()) if kind.startswith("joint") else None,
        "dependents": [draw(people(adult=False)) for _ in range(n_dependents)],
        "supplied_deduction": draw(st.integers(0, 30_000)),
    }


def _entries(unit):
    entries = [("head", unit["head"])]
    if unit["spouse"] is not None:
        entries.append(("spouse", unit["spouse"]))
    return entries + [("dependent", d) for d in unit["dependents"]]


VARIANTS = ["base", "raised"]


def _situation(units, year, supplied_deduction, supplied_subtotal=False):
    people_, tax_units_, households, marital_units = {}, {}, {}, {}
    for variant in VARIANTS:
        for i, unit in enumerate(units):
            names, couple = [], []
            for j, (role, values) in enumerate(_entries(unit)):
                name = f"{variant}_{i}_{j}"
                names.append(name)
                long_term_care = values["long_term_care"] + (
                    values["long_term_care_rise"] if variant == "raised" else 0
                )
                people_[name] = {
                    key: {year: value}
                    for key, value in {
                        "age": values["age"],
                        "is_tax_unit_head": role == "head",
                        "is_tax_unit_spouse": role == "spouse",
                        "is_tax_unit_dependent": role == "dependent",
                        "is_self_employed": values["self_employed"],
                        "self_employment_income": values["earnings"],
                        "medicare_enrolled": False,
                        "health_insurance_premiums": values["health_premiums"],
                        "long_term_health_insurance_premiums": long_term_care,
                        "other_medical_expenses": values["other"],
                    }.items()
                }
                if role == "dependent":
                    marital_units[f"{name}_single"] = {"members": [name]}
                else:
                    couple.append(name)
            marital_units[f"{variant}_{i}_couple"] = {"members": couple}
            tax_unit = {"members": names}
            if supplied_deduction:
                tax_unit["self_employed_health_insurance_ald"] = {
                    year: unit["supplied_deduction"]
                }
            if supplied_subtotal:
                tax_unit["itemized_medical_expenses"] = {year: 1_000}
            tax_units_[f"{variant}_{i}_tax_unit"] = tax_unit
            households[f"{variant}_{i}_household"] = {
                "members": names,
                "state_code": {year: "TX"},
            }
    return {
        "people": people_,
        "tax_units": tax_units_,
        "households": households,
        "marital_units": marital_units,
    }


PERSON_VARIABLES = [
    "eligible_long_term_care_premiums",
    "self_employed_health_insurance_ald_person",
    "is_tax_unit_dependent",
]
UNIT_VARIABLES = [
    "self_employed_health_insurance_ald",
    "itemized_medical_expenses_excluded_premiums",
    "itemized_medical_expenses_excluded_long_term_care_premiums",
    "itemized_medical_expenses_applied_exclusion",
    "itemized_medical_expenses_long_term_care_premiums",
    "itemized_medical_expenses",
]


def _run(units, year, supplied_deduction):
    sim = Simulation(
        tax_benefit_system=system,
        situation=_situation(units, year, supplied_deduction),
    )
    out = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in PERSON_VARIABLES + UNIT_VARIABLES
    }
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _person_inputs(units):
    rows = []
    for variant in VARIANTS:
        for unit in units:
            for role, values in _entries(unit):
                long_term_care = values["long_term_care"] + (
                    values["long_term_care_rise"] if variant == "raised" else 0
                )
                rows.append(
                    (
                        values["age"],
                        role != "dependent",
                        values["self_employed"],
                        values["earnings"],
                        values["health_premiums"],
                        long_term_care,
                        values["other"],
                    )
                )
    return np.array(rows, dtype=float).T


def _check(units, year, supplied_deduction):
    run = _run(units, year, supplied_deduction)
    age, filer, self_employed, earnings, health, long_term_care, other = _person_inputs(
        units
    )
    unit = run["unit"]
    n_units = unit.max() + 1

    def unit_sum(values):
        return np.bincount(unit, weights=values, minlength=n_units)

    # 1. Eligible premiums: min(premiums, published limit), within bounds.
    eligible = run["eligible_long_term_care_premiums"]
    if year in PUBLISHED_LIMITS:
        limit = np.array([_published_limit(year, a) for a in age])
        np.testing.assert_allclose(
            eligible, np.minimum(long_term_care, limit), atol=TOLERANCE
        )
    assert (eligible >= 0).all()
    assert (eligible <= long_term_care + TOLERANCE).all()

    # 2. The exclusion takes medical premiums first, then eligible premiums.
    deduction = np.maximum(run["self_employed_health_insurance_ald"], 0)
    filer_health = unit_sum(health * filer)
    filer_eligible = unit_sum(eligible * filer)
    medical_part = np.minimum(filer_health, deduction)
    long_term_care_part = np.minimum(filer_eligible, deduction - medical_part)
    np.testing.assert_allclose(
        run["itemized_medical_expenses_excluded_premiums"],
        medical_part,
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        run["itemized_medical_expenses_excluded_long_term_care_premiums"],
        long_term_care_part,
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        medical_part + long_term_care_part,
        np.minimum(filer_health + filer_eligible, deduction),
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        run["itemized_medical_expenses_applied_exclusion"],
        medical_part + long_term_care_part,
        atol=TOLERANCE,
    )

    # 3. Accounting identity for the subtotal, from the raw inputs.
    inside = run["itemized_medical_expenses_long_term_care_premiums"]
    all_eligible = unit_sum(eligible)
    np.testing.assert_allclose(
        inside, all_eligible - long_term_care_part, atol=TOLERANCE
    )
    assert (inside >= unit_sum(eligible * ~filer.astype(bool)) - TOLERANCE).all()
    assert (inside <= all_eligible + TOLERANCE).all()
    subtotal = run["itemized_medical_expenses"]
    np.testing.assert_allclose(
        subtotal,
        unit_sum(health) - medical_part + inside + unit_sum(other),
        atol=TOLERANCE,
    )

    if not supplied_deduction:
        # 4. Each eligible premium is deducted once.
        np.testing.assert_allclose(
            subtotal - unit_sum(other) + run["self_employed_health_insurance_ald"],
            unit_sum(health) + all_eligible,
            atol=TOLERANCE,
        )
        # 5. The derived person deduction (Form 7206 lines 1-3).
        np.testing.assert_allclose(
            run["self_employed_health_insurance_ald_person"],
            self_employed * np.minimum(np.maximum(earnings, 0), health + eligible),
            atol=TOLERANCE,
        )

    # 6. Monotonicity in long-term care premiums.
    half = n_units // 2
    base, raised = slice(0, half), slice(half, n_units)
    rise_in_eligible = all_eligible[raised] - all_eligible[base]
    rise_in_subtotal = subtotal[raised] - subtotal[base]
    assert (rise_in_subtotal >= -TOLERANCE).all()
    assert (rise_in_subtotal <= rise_in_eligible + TOLERANCE).all()
    no_deduction = (deduction[base] == 0) & (deduction[raised] == 0)
    np.testing.assert_allclose(
        rise_in_subtotal[no_deduction],
        rise_in_eligible[no_deduction],
        atol=TOLERANCE,
    )


SETTINGS = dict(max_examples=10, deadline=None, derandomize=True)
YEARS = list(range(2015, LAST_PUBLISHED + 4))


@settings(**SETTINGS)
@given(
    st.sampled_from(YEARS),
    st.booleans(),
    st.lists(tax_units(), min_size=3, max_size=12),
)
def test_long_term_care_premium_properties(year, supplied_deduction, units):
    _check(units, year, supplied_deduction)


@pytest.mark.parametrize("year", [2018, 2022, 2025])
@pytest.mark.parametrize("supplied_deduction", [False, True])
def test_seeded_population(year, supplied_deduction):
    rng = np.random.default_rng(20261018 + year)

    def person(adult=True):
        self_employed = bool(rng.random() < 0.4)
        return {
            "age": int(rng.choice(EDGE_AGES[2:] if adult else EDGE_AGES)),
            "self_employed": self_employed,
            "earnings": int(rng.integers(-10_000, 60_001)) if self_employed else 0,
            "health_premiums": int(rng.integers(0, 15_001)),
            "long_term_care": int(rng.integers(0, 12_001)) * (rng.random() < 0.7),
            "long_term_care_rise": int(rng.integers(0, 8_001)),
            "other": int(rng.integers(0, 15_001)),
        }

    units = []
    for _ in range(60):
        kind = rng.choice(["single", "joint", "joint_dependents", "hoh"])
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("joint_dependents", "hoh") else 0
        )
        units.append(
            {
                "head": person(),
                "spouse": person() if kind.startswith("joint") else None,
                "dependents": [person(adult=False) for _ in range(n_dependents)],
                "supplied_deduction": int(rng.integers(0, 30_001)),
            }
        )
    _check(units, year, supplied_deduction)


def test_supplied_subtotal_holds_no_computed_long_term_care_premiums():
    units = [
        {
            "head": {
                "age": 75,
                "self_employed": True,
                "earnings": 40_000,
                "health_premiums": 2_000,
                "long_term_care": 9_000,
                "long_term_care_rise": 0,
                "other": 500,
            },
            "spouse": None,
            "dependents": [],
            "supplied_deduction": 0,
        }
    ]
    sim = Simulation(
        tax_benefit_system=system,
        situation=_situation(units, 2025, False, supplied_subtotal=True),
    )
    np.testing.assert_array_equal(
        sim.calculate("itemized_medical_expenses_long_term_care_premiums", 2025), 0
    )
    np.testing.assert_array_equal(
        sim.calculate("itemized_medical_expenses_applied_exclusion", 2025), 0
    )
    np.testing.assert_array_equal(
        sim.calculate("itemized_medical_expenses", 2025), 1_000
    )
