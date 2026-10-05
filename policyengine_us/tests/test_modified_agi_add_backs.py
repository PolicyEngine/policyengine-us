"""Property and differential tests for the modified AGI add-backs of 26 U.S.C.
sections 911, 931 and 933.

26 U.S.C. 221(b)(2)(C) defines the modified adjusted gross income of the
student loan interest deduction as adjusted gross income "determined (i)
without regard to this section and sections 85(c), 911, 931, and 933, and
(ii) after application of sections 86, 135, 137, 219, and 469". Sections
24(b)(1), 25A(d)(2), 25B(e), 25E(b)(3), 30D(f)(10)(C), 151(d)(5)(C),
163(h)(4)(C), 164(b)(7)(B), 224(b)(2)(B) and 225(b)(2)(B) each use adjusted
gross income increased by any amount excluded under sections 911, 931 or
933; the model computes that once, as
`agi_plus_section_911_931_933_exclusions`. Section 86(b)(2) (taxable Social
Security) and section 1411(d) (net investment income tax) add back the
section 911 exclusion too.

In the model, income inputs are net of the section 911 exclusion, and
sections 931 and 933 are above-the-line deductions. A household with
possession or Puerto Rico income therefore reports it in wages and deducts
it again.

Two kinds of test, on random households:

- Differential. Student-loan MAGI is built from gross income sources with
  the excluded deductions left in; adjusted gross income is built from
  gross income less every deduction. On every return, MAGI must equal AGI
  plus the student loan interest deduction, the three excluded amounts, and
  any unemployment compensation section 85(c) excluded (2020). The shared
  modified AGI must equal AGI plus the three excluded amounts.
- Shifting income into an excluded category while every other part of AGI
  stays fixed (raising the section 911 exclusion, or raising wages together
  with the section 931 or 933 deduction) raises student-loan MAGI by exactly
  the amount shifted, never raises the student loan interest deduction, and
  moves every phase-out the shared modified AGI feeds in one direction only:
  no reduction falls and no deduction, cap or eligibility rises. AGI itself
  moves only by the fall in the student loan interest deduction and, in
  2020, by any unemployment compensation that fall makes taxable.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

# Hypothesis is a dev extra; skip rather than fail collection without it.
hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

STATUSES = ["SINGLE", "JOINT", "HEAD_OF_HOUSEHOLD"]
EXCLUSIONS = [
    "foreign_earned_income_exclusion",
    "specified_possession_income",
    "puerto_rico_income",
]
YEARS = [2020, 2024, 2025, 2026]

# Outputs that must not fall when excluded income rises (reductions).
NON_DECREASING = [
    "ctc_phase_out",
    "education_credit_phase_out",
    "lifetime_learning_credit_phase_out",
]
# Outputs that must not rise (deductions, caps, eligibility).
NON_INCREASING = [
    "student_loan_interest_ald",
    "tip_income_deduction",
    "overtime_income_deduction",
    "auto_loan_interest_deduction",
    "salt_cap",
    "new_clean_vehicle_credit_eligible",
    "used_clean_vehicle_credit_eligible",
]
TAX_UNIT_OUTPUTS = [
    "adjusted_gross_income",
    "agi_plus_section_911_931_933_exclusions",
    "additional_senior_deduction_magi",
    "tax_unit_taxable_unemployment_compensation",
    "taxable_ss_magi",
    "niit_magi",
    *NON_DECREASING,
    *NON_INCREASING,
]
# Person-level outputs summed over the return.
SUMMED_OUTPUTS = [
    "student_loan_interest_ald_magi",
    "student_loan_interest_ald",
    "unemployment_compensation",
]


def build_situation(households, year):
    people, tax_units, marital_units = {}, {}, {}
    groups = {"households": {}, "spm_units": {}, "families": {}}
    for i, h in enumerate(households):
        head = f"head_{i}"
        people[head] = {
            "age": {year: 40},
            # Possession and Puerto Rico income is part of wages and is
            # deducted again above the line.
            "employment_income": {
                year: h["wages"]
                + h["specified_possession_income"]
                + h["puerto_rico_income"]
            },
            "unemployment_compensation": {year: h["unemployment_compensation"]},
            "student_loan_interest": {year: h["student_loan_interest"]},
            "tip_income": {year: h["tips"]},
            "treasury_tipped_occupation_code": {year: 102},
            "fsla_overtime_premium": {year: h["overtime"]},
            "real_estate_taxes": {year: h["real_estate_taxes"]},
        }
        members = [head]
        marital_units[f"marital_unit_{i}"] = {"members": [head]}
        if h["status"] == "JOINT":
            spouse = f"spouse_{i}"
            people[spouse] = {
                "age": {year: 40},
                "employment_income": {year: h["spouse_wages"]},
            }
            members.append(spouse)
            marital_units[f"marital_unit_{i}"]["members"].append(spouse)
        if h["status"] == "HEAD_OF_HOUSEHOLD":
            child = f"child_{i}"
            people[child] = {"age": {year: 10}}
            members.append(child)
            marital_units[f"marital_unit_{i}_child"] = {"members": [child]}
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            # Set for every tax unit so none falls back to the default.
            "filing_status": {year: h["status"]},
            "foreign_earned_income_exclusion": {
                year: h["foreign_earned_income_exclusion"]
            },
            "specified_possession_income": {year: h["specified_possession_income"]},
            "puerto_rico_income": {year: h["puerto_rico_income"]},
            "tip_income_deduction_ssn_requirement_met": {year: True},
            "overtime_income_deduction_ssn_requirement_met": {year: True},
            "purchased_qualifying_new_clean_vehicle": {year: h["bought_vehicle"]},
            "new_clean_vehicle_battery_capacity": {year: 10},
            "new_clean_vehicle_msrp": {year: 40_000},
            "purchased_qualifying_used_clean_vehicle": {year: h["bought_vehicle"]},
        }
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "TX"},
            "qualified_passenger_vehicle_loan_interest": {year: h["car_loan_interest"]},
        }
        groups["spm_units"][f"spm_unit_{i}"] = {"members": members}
        groups["families"][f"family_{i}"] = {"members": members}
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        **groups,
    }


def calculate(households, year):
    simulation = Simulation(situation=build_situation(households, year))
    results = {
        v: np.asarray(simulation.calculate(v, year), dtype=float)
        for v in TAX_UNIT_OUTPUTS
    }
    for v in SUMMED_OUTPUTS:
        results[v] = np.asarray(
            simulation.calculate(v, year, map_to="tax_unit"), dtype=float
        )
    return results


def shifted(household, category, amount):
    """The same household with `amount` more income in an excluded category.

    The section 911 exclusion is not in the income inputs, so raising it
    leaves AGI alone. Section 931 and 933 income is in wages and deducted
    again, so raising it raises both and leaves AGI alone.
    """
    return {**household, category: household[category] + amount}


def tolerance(*amounts):
    # Single-precision storage: allow a few units in the last place.
    return 1 + 1e-6 * max(abs(a) for a in amounts)


def assert_differential(households, results):
    for i, h in enumerate(households):
        r = {v: results[v][i] for v in results}
        excluded = sum(h[c] for c in EXCLUSIONS)
        uc_excluded = (
            r["unemployment_compensation"]
            - r["tax_unit_taxable_unemployment_compensation"]
        )
        expected = (
            r["adjusted_gross_income"]
            + r["student_loan_interest_ald"]
            + excluded
            + uc_excluded
        )
        assert r["student_loan_interest_ald_magi"] == pytest.approx(
            expected, abs=tolerance(expected)
        ), (h, r)
        assert r["agi_plus_section_911_931_933_exclusions"] == pytest.approx(
            r["adjusted_gross_income"] + excluded,
            abs=tolerance(r["adjusted_gross_income"], excluded),
        ), (h, r)
        assert (
            r["additional_senior_deduction_magi"]
            == r["agi_plus_section_911_931_933_exclusions"]
        ), (h, r)
        # The deduction is capped at the interest paid and $2,500.
        assert (
            0
            <= r["student_loan_interest_ald"]
            <= min(h["student_loan_interest"], 2_500) + tolerance(2_500)
        ), (h, r)


def assert_shift_invariants(households, shifts, year):
    pairs = []
    for h, (category, amount) in zip(households, shifts):
        pairs += [h, shifted(h, category, amount)]
    results = calculate(pairs, year)
    assert_differential(pairs, results)
    base = {v: a[0::2] for v, a in results.items()}
    more = {v: a[1::2] for v, a in results.items()}
    for i, (h, (category, amount)) in enumerate(zip(households, shifts)):
        context = (h, category, amount, year)
        b = {v: base[v][i] for v in base}
        m = {v: more[v][i] for v in more}
        # Student-loan MAGI rises by exactly the amount shifted.
        rise = m["student_loan_interest_ald_magi"] - b["student_loan_interest_ald_magi"]
        assert rise == pytest.approx(
            amount, abs=tolerance(m["student_loan_interest_ald_magi"])
        ), context
        # AGI moves only through the student loan interest deduction and,
        # in 2020, the unemployment compensation its fall makes taxable
        # (the section 85(c) income test subtracts the deduction).
        agi_change = m["adjusted_gross_income"] - b["adjusted_gross_income"]
        deduction_change = (
            b["student_loan_interest_ald"] - m["student_loan_interest_ald"]
        )
        taxable_uc_change = (
            m["tax_unit_taxable_unemployment_compensation"]
            - b["tax_unit_taxable_unemployment_compensation"]
        )
        assert deduction_change >= -tolerance(2_500), context
        assert agi_change == pytest.approx(
            deduction_change + taxable_uc_change,
            abs=tolerance(m["adjusted_gross_income"]),
        ), context
        # Section 86(b)(2) MAGI adds back all three and has no deduction for
        # student loan interest, so it rises by exactly the amount shifted.
        ss_rise = m["taxable_ss_magi"] - b["taxable_ss_magi"]
        assert ss_rise == pytest.approx(amount, abs=tolerance(m["taxable_ss_magi"])), (
            context
        )
        slack = 1e-6
        for v in NON_DECREASING + ["agi_plus_section_911_931_933_exclusions"]:
            assert m[v] >= b[v] - slack * max(1, abs(b[v])), (v, context)
        for v in NON_INCREASING:
            assert m[v] <= b[v] + slack * max(1, abs(b[v])), (v, context)
        # Section 1411(d) adds back only section 911.
        niit_rise = m["niit_magi"] - b["niit_magi"]
        expected_niit_rise = agi_change + (
            amount if category == "foreign_earned_income_exclusion" else 0
        )
        assert niit_rise == pytest.approx(
            expected_niit_rise, abs=tolerance(m["niit_magi"])
        ), context


household_strategy = st.fixed_dictionaries(
    {
        "status": st.sampled_from(STATUSES),
        "wages": st.integers(0, 400_000),
        "spouse_wages": st.one_of(st.just(0), st.integers(1, 200_000)),
        "unemployment_compensation": st.one_of(st.just(0), st.integers(1, 30_000)),
        "student_loan_interest": st.one_of(st.just(0), st.integers(1, 4_000)),
        "foreign_earned_income_exclusion": st.one_of(
            st.just(0), st.integers(1, 130_000)
        ),
        "specified_possession_income": st.one_of(st.just(0), st.integers(1, 100_000)),
        "puerto_rico_income": st.one_of(st.just(0), st.integers(1, 100_000)),
        "tips": st.one_of(st.just(0), st.integers(1, 30_000)),
        "overtime": st.one_of(st.just(0), st.integers(1, 20_000)),
        "car_loan_interest": st.one_of(st.just(0), st.integers(1, 12_000)),
        "real_estate_taxes": st.one_of(st.just(0), st.integers(1, 60_000)),
        "bought_vehicle": st.booleans(),
    }
)
shift_strategy = st.tuples(st.sampled_from(EXCLUSIONS), st.integers(1, 100_000))

# Households in each phase-out range, so the shift crosses a threshold.
GRID = [
    # 2024 student loan phase-out: $80,000-$95,000 single.
    dict(
        status="SINGLE",
        wages=75_000,
        spouse_wages=0,
        unemployment_compensation=0,
        student_loan_interest=2_500,
        foreign_earned_income_exclusion=0,
        specified_possession_income=0,
        puerto_rico_income=0,
        tips=10_000,
        overtime=10_000,
        car_loan_interest=5_000,
        real_estate_taxes=50_000,
        bought_vehicle=True,
    ),
    # Joint, with unemployment compensation and all three exclusions.
    dict(
        status="JOINT",
        wages=120_000,
        spouse_wages=30_000,
        unemployment_compensation=8_000,
        student_loan_interest=3_000,
        foreign_earned_income_exclusion=5_000,
        specified_possession_income=4_000,
        puerto_rico_income=3_000,
        tips=0,
        overtime=15_000,
        car_loan_interest=9_000,
        real_estate_taxes=20_000,
        bought_vehicle=True,
    ),
    # Head of household near the tip, overtime and car loan phase-outs.
    dict(
        status="HEAD_OF_HOUSEHOLD",
        wages=140_000,
        spouse_wages=0,
        unemployment_compensation=0,
        student_loan_interest=1_000,
        foreign_earned_income_exclusion=0,
        specified_possession_income=0,
        puerto_rico_income=0,
        tips=20_000,
        overtime=10_000,
        car_loan_interest=10_000,
        real_estate_taxes=0,
        bought_vehicle=False,
    ),
    # High income, near the SALT cap phase-down and the CTC phase-out.
    dict(
        status="SINGLE",
        wages=480_000,
        spouse_wages=0,
        unemployment_compensation=0,
        student_loan_interest=0,
        foreign_earned_income_exclusion=0,
        specified_possession_income=0,
        puerto_rico_income=0,
        tips=0,
        overtime=0,
        car_loan_interest=0,
        real_estate_taxes=60_000,
        bought_vehicle=False,
    ),
]
GRID_SHIFTS = [(category, 15_000) for category in EXCLUSIONS]


@pytest.mark.parametrize("year", YEARS)
def test_grid_keeps_the_invariants(year):
    households = [h for h in GRID for _ in GRID_SHIFTS]
    shifts = [s for _ in GRID for s in GRID_SHIFTS]
    assert_shift_invariants(households, shifts, year)


def test_unemployment_excluded_in_2020_counts_toward_student_loan_magi():
    # 2020: section 85(c) excludes up to $10,200 of unemployment compensation
    # from gross income; section 221(b)(2)(C)(i) disregards that exclusion.
    household = {**GRID[0], "wages": 60_000, "unemployment_compensation": 10_000}
    results = calculate([household], 2020)
    assert results["tax_unit_taxable_unemployment_compensation"][0] == 0
    assert results["student_loan_interest_ald_magi"][0] == pytest.approx(70_000)
    assert_differential([household], results)


SETTINGS = dict(
    max_examples=10,
    deadline=None,
    suppress_health_check=[
        hypothesis.HealthCheck.too_slow,
        hypothesis.HealthCheck.data_too_large,
    ],
)


@hypothesis.settings(**SETTINGS)
@hypothesis.given(
    st.lists(st.tuples(household_strategy, shift_strategy), min_size=1, max_size=15),
    st.sampled_from(YEARS),
)
def test_random_households_keep_the_invariants(cases, year):
    households = [h for h, _ in cases]
    shifts = [s for _, s in cases]
    assert_shift_invariants(households, shifts, year)
