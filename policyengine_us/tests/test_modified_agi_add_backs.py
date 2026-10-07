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
Security) adds back all three as well.

In the model, income inputs are net of the section 911 exclusion, and
sections 931 and 933 are above-the-line deductions. A household with
possession or Puerto Rico income therefore reports it in wages and deducts
it again. The section 911 amount comes in two sizes. Modified AGIs add back
Form 2555 lines 45 and 50 (`section_911_excluded_income`). The section
911(f) rate stacking uses that amount less deductions disallowed because
they relate to the excluded income (`foreign_earned_income_exclusion`,
Foreign Earned Income Tax Worksheet line 2c). Random households set both.

Two kinds of test, on random households:

- Differential. Student-loan MAGI is built from gross income sources with
  the excluded deductions left in; adjusted gross income is built from
  gross income less every deduction. On every return, MAGI must equal AGI
  plus the student loan interest deduction, the three excluded amounts, and
  any unemployment compensation section 85(c) excluded (2020). The shared
  modified AGI must equal AGI plus the three excluded amounts, and the
  Medicaid and ACA modified AGI must equal AGI plus the section 911 amount;
  each takes Form 2555 lines 45 and 50 in full. The rate stacking adds the
  amount net of disallowed deductions to taxable income. A clean vehicle
  credit is income-eligible exactly when the lesser of this year's and the
  preceding year's modified AGI is within the limit.
- Shifting income into an excluded category while every other part of AGI
  stays fixed (raising the section 911 exclusion, raising the deductions it
  disallows, or raising wages together with the section 931 or 933
  deduction) raises student-loan MAGI by exactly
  the amount shifted, never raises the student loan interest deduction, and
  moves every phase-out the shared modified AGI feeds in one direction only:
  no reduction falls and no deduction, cap or eligibility rises. AGI itself
  moves only by the fall in the student loan interest deduction and, in
  2020, by any unemployment compensation that fall makes taxable.

A third test checks the Medicare IRMAA modified AGI of 42 U.S.C.
1395r(i)(4), from income two years before the benefit year. With AGI
provided, it equals AGI plus the head's and spouse's tax-exempt interest,
every member's section 135 exclusion, and the section 911 (Form 2555 lines
45 and 50), 931 and 933 amounts. A dependent's own tax-exempt interest is on
the dependent's return, as the rest of the dependent's income is. AGI
deducts the section 135 exclusion wherever it is recorded in the tax unit
(`gov.irs.ald.filer_amounts_recorded_on_dependents`): only a bond issued to
an owner aged 24 or older qualifies (section 135(c)(1)(B)), so an amount
recorded on a dependent is the filer's exclusion for the dependent's
tuition. With AGI computed from wages, the IRMAA MAGI therefore does not
depend on section 135 amounts at all.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

# Hypothesis is a dev extra; skip rather than fail collection without it.
hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

STATUSES = ["SINGLE", "JOINT", "HEAD_OF_HOUSEHOLD"]
# Excluded-income categories a household can shift income into. The section
# 911 amount added back is Form 2555 lines 45 and 50: the rate stacking
# amount plus the deductions disallowed because they relate to it.
EXCLUSIONS = [
    "foreign_earned_income_exclusion",
    "section_911_disallowed_deductions",
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
    "medicaid_magi",
    "taxable_income",
    "taxable_income_plus_section_911_exclusion",
    "additional_senior_deduction_magi",
    "tax_unit_taxable_unemployment_compensation",
    "taxable_ss_magi",
    *NON_DECREASING,
    *NON_INCREASING,
]
# Person-level outputs summed over the return.
SUMMED_OUTPUTS = [
    "student_loan_interest_ald_magi",
    "student_loan_interest_ald",
    "unemployment_compensation",
]


# An input given for any tax unit in a simulation is set for all of them; the
# others take the variable's default value, not its formula. So a batch
# supplies each defaulted input for every tax unit or for none.
def sets_section_911_amount(households):
    """Whether the batch supplies the Form 2555 amount.

    It must when any household has disallowed deductions. Otherwise the
    batch may leave it to default to the stacking amount.
    """
    return any(
        h["section_911_disallowed_deductions"] or h["set_section_911_amount"]
        for h in households
    )


# Over every income limit: with this as the preceding year's modified AGI,
# this year's alone decides, as when the input is not provided.
NO_PRIOR_YEAR_MAGI = 10**9


def build_situation(households, year):
    set_911 = sets_section_911_amount(households)
    set_prior = any(h["prior_year_magi"] is not None for h in households)
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
        if set_911:
            # Otherwise the Form 2555 amount defaults to the stacking amount.
            tax_units[f"tax_unit_{i}"]["section_911_excluded_income"] = {
                year: section_911_excluded_income(h)
            }
        if set_prior:
            prior = h["prior_year_magi"]
            tax_units[f"tax_unit_{i}"]["clean_vehicle_credit_prior_year_magi"] = {
                year: NO_PRIOR_YEAR_MAGI if prior is None else prior
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


def section_911_excluded_income(h):
    # Form 2555 lines 45 and 50 (Foreign Earned Income Tax Worksheet line
    # 2a), from line 2c and the disallowed deductions on line 2b.
    return h["foreign_earned_income_exclusion"] + h["section_911_disallowed_deductions"]


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
    # Each household's clean vehicle income limits and whether the credits
    # are in effect, to check the lesser-of test.
    p = simulation.tax_benefit_system.parameters(year).gov.irs.credits.clean_vehicle
    for credit, eligibility in [
        ("new", p.new.eligibility),
        ("used", p.used.eligibility),
    ]:
        results[f"{credit}_income_limit"] = np.array(
            [eligibility.income_limit[h["status"]] for h in households], dtype=float
        )
        results[f"{credit}_in_effect"] = np.full(
            len(households), float(eligibility.in_effect)
        )
    return results


def shifted(household, category, amount):
    """The same household with `amount` more income in an excluded category.

    The section 911 exclusion is not in the income inputs, so raising it, or
    the deductions it disallows, leaves AGI alone. Section 931 and 933
    income is in wages and deducted again, so raising it raises both and
    leaves AGI alone.
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
        # Medicaid and ACA modified AGI adds back only section 911 (and
        # tax-exempt interest and Social Security, which these households
        # lack), also as Form 2555 lines 45 and 50.
        section_911 = section_911_excluded_income(h)
        assert r["medicaid_magi"] == pytest.approx(
            max(0, r["adjusted_gross_income"] + section_911),
            abs=tolerance(r["adjusted_gross_income"], section_911),
        ), (h, r)
        # The rate stacking adds the amount net of disallowed deductions.
        stacked = r["taxable_income_plus_section_911_exclusion"] - r["taxable_income"]
        assert stacked == pytest.approx(
            h["foreign_earned_income_exclusion"],
            abs=tolerance(r["taxable_income_plus_section_911_exclusion"]),
        ), (h, r)
        # Clean vehicles: income-eligible when the lesser of this year's and
        # the preceding year's modified AGI is within the limit. Without a
        # preceding-year amount, this year's decides.
        magi = r["agi_plus_section_911_931_933_exclusions"]
        prior = magi if h["prior_year_magi"] is None else h["prior_year_magi"]
        for credit in ["new", "used"]:
            expected = (
                h["bought_vehicle"]
                and r[f"{credit}_in_effect"] == 1
                and min(magi, prior) <= r[f"{credit}_income_limit"]
            )
            assert r[f"{credit}_clean_vehicle_credit_eligible"] == expected, (
                credit,
                h,
                r,
            )
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
        "section_911_disallowed_deductions": st.one_of(
            st.just(0), st.integers(1, 40_000)
        ),
        # Whether to supply the Form 2555 amount when no deductions are
        # disallowed, or leave it to default to the stacking amount.
        "set_section_911_amount": st.booleans(),
        "specified_possession_income": st.one_of(st.just(0), st.integers(1, 100_000)),
        "puerto_rico_income": st.one_of(st.just(0), st.integers(1, 100_000)),
        "tips": st.one_of(st.just(0), st.integers(1, 30_000)),
        "overtime": st.one_of(st.just(0), st.integers(1, 20_000)),
        "car_loan_interest": st.one_of(st.just(0), st.integers(1, 12_000)),
        "real_estate_taxes": st.one_of(st.just(0), st.integers(1, 60_000)),
        "bought_vehicle": st.booleans(),
        "prior_year_magi": st.one_of(st.none(), st.integers(0, 400_000)),
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
        section_911_disallowed_deductions=0,
        set_section_911_amount=False,
        specified_possession_income=0,
        puerto_rico_income=0,
        tips=10_000,
        overtime=10_000,
        car_loan_interest=5_000,
        real_estate_taxes=50_000,
        bought_vehicle=True,
        prior_year_magi=None,
    ),
    # Joint, with unemployment compensation and all three exclusions.
    dict(
        status="JOINT",
        wages=120_000,
        spouse_wages=30_000,
        unemployment_compensation=8_000,
        student_loan_interest=3_000,
        foreign_earned_income_exclusion=5_000,
        section_911_disallowed_deductions=2_000,
        set_section_911_amount=True,
        specified_possession_income=4_000,
        puerto_rico_income=3_000,
        tips=0,
        overtime=15_000,
        car_loan_interest=9_000,
        real_estate_taxes=20_000,
        bought_vehicle=True,
        # Under the $150,000 joint limit for used vehicles; this year's
        # modified AGI is over it.
        prior_year_magi=140_000,
    ),
    # Head of household near the tip, overtime and car loan phase-outs.
    dict(
        status="HEAD_OF_HOUSEHOLD",
        wages=140_000,
        spouse_wages=0,
        unemployment_compensation=0,
        student_loan_interest=1_000,
        foreign_earned_income_exclusion=0,
        section_911_disallowed_deductions=0,
        set_section_911_amount=False,
        specified_possession_income=0,
        puerto_rico_income=0,
        tips=20_000,
        overtime=10_000,
        car_loan_interest=10_000,
        real_estate_taxes=0,
        bought_vehicle=False,
        prior_year_magi=None,
    ),
    # High income, near the SALT cap phase-down and the CTC phase-out.
    dict(
        status="SINGLE",
        wages=480_000,
        spouse_wages=0,
        unemployment_compensation=0,
        student_loan_interest=0,
        foreign_earned_income_exclusion=0,
        section_911_disallowed_deductions=0,
        set_section_911_amount=False,
        specified_possession_income=0,
        puerto_rico_income=0,
        tips=0,
        overtime=0,
        car_loan_interest=0,
        real_estate_taxes=60_000,
        bought_vehicle=True,
        # Under the $150,000 single limit for new vehicles, over the $75,000
        # used-vehicle limit; this year's modified AGI is over both.
        prior_year_magi=140_000,
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


# Medicare IRMAA: households whose income two years before the benefit year
# is either provided as AGI or computed from wages. 2016 looks back to 2014,
# before the model's first year, where only provided amounts count.
IRMAA_YEARS = [2016, 2017, 2026]
# Benefit years whose lag year the model computes.
IRMAA_COMPUTED_YEARS = [2017, 2026]

irmaa_household_strategy = st.fixed_dictionaries(
    {
        "joint": st.booleans(),
        "has_dependent": st.booleans(),
        "agi": st.integers(0, 600_000),
        "wages": st.integers(0, 400_000),
        "spouse_wages": st.one_of(st.just(0), st.integers(1, 200_000)),
        "tax_exempt_interest": st.one_of(st.just(0), st.integers(1, 20_000)),
        "spouse_tax_exempt_interest": st.one_of(st.just(0), st.integers(1, 20_000)),
        "dependent_tax_exempt_interest": st.one_of(st.just(0), st.integers(1, 20_000)),
        "head_bonds": st.one_of(st.just(0), st.integers(1, 10_000)),
        "spouse_bonds": st.one_of(st.just(0), st.integers(1, 10_000)),
        "dependent_bonds": st.one_of(st.just(0), st.integers(1, 10_000)),
        "foreign_earned_income_exclusion": st.one_of(
            st.just(0), st.integers(1, 130_000)
        ),
        "section_911_disallowed_deductions": st.one_of(
            st.just(0), st.integers(1, 40_000)
        ),
        "set_section_911_amount": st.booleans(),
        "specified_possession_income": st.one_of(st.just(0), st.integers(1, 50_000)),
        "puerto_rico_income": st.one_of(st.just(0), st.integers(1, 50_000)),
    }
)


def build_irmaa_situation(households, year, computed):
    """Households for an IRMAA benefit year.

    With `computed`, the lag year's AGI comes from wages, which include any
    possession and Puerto Rico income (deducted again above the line).
    Otherwise AGI is provided for the lag year. Ages are set for both years,
    so the lag year's tax unit roles (which decide whose tax-exempt interest
    is on the return) are the benefit year's; age defaults to 40 otherwise.
    """
    lag = year - 2
    set_911 = sets_section_911_amount(households)
    people, tax_units, marital_units = {}, {}, {}
    groups = {"households": {}, "spm_units": {}, "families": {}}

    def person(age, bonds, interest, wages=0):
        # An input carries forward to later years it is not supplied for, so
        # the benefit year's amounts are set to zero.
        p = {
            "age": {lag: age - 2, year: age},
            "us_bonds_for_higher_ed": {lag: bonds, year: 0},
            "tax_exempt_interest_income": {lag: interest, year: 0},
        }
        if computed:
            p["employment_income"] = {lag: wages, year: 0}
        return p

    for i, h in enumerate(households):
        head = f"head_{i}"
        people[head] = person(
            66,
            h["head_bonds"],
            h["tax_exempt_interest"],
            h["wages"] + h["specified_possession_income"] + h["puerto_rico_income"],
        )
        members = [head]
        marital_units[f"marital_unit_{i}"] = {"members": [head]}
        if h["joint"]:
            spouse = f"spouse_{i}"
            people[spouse] = person(
                64,
                h["spouse_bonds"],
                h["spouse_tax_exempt_interest"],
                h["spouse_wages"],
            )
            members.append(spouse)
            marital_units[f"marital_unit_{i}"]["members"].append(spouse)
        if h["has_dependent"]:
            child = f"child_{i}"
            people[child] = person(
                15, h["dependent_bonds"], h["dependent_tax_exempt_interest"]
            )
            members.append(child)
            marital_units[f"marital_unit_{i}_child"] = {"members": [child]}
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            "foreign_earned_income_exclusion": {
                lag: h["foreign_earned_income_exclusion"]
            },
            "specified_possession_income": {lag: h["specified_possession_income"]},
            "puerto_rico_income": {lag: h["puerto_rico_income"]},
        }
        if not computed:
            tax_units[f"tax_unit_{i}"]["adjusted_gross_income"] = {lag: h["agi"]}
        if set_911:
            tax_units[f"tax_unit_{i}"]["section_911_excluded_income"] = {
                lag: section_911_excluded_income(h)
            }
        for group in groups:
            groups[group][f"{group}_{i}"] = {"members": members}
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        **groups,
    }


def assert_irmaa_identity(households, year, computed):
    simulation = Simulation(situation=build_irmaa_situation(households, year, computed))
    magi = simulation.calculate("medicare_irmaa_magi_two_years_prior", year)
    for i, h in enumerate(households):
        # 42 U.S.C. 1395r(i)(4)(A): AGI without regard to sections 135, 911,
        # 931 and 933, plus tax-exempt interest on the return. AGI deducts the
        # section 135 exclusion wherever it is recorded in the tax unit, and
        # the IRMAA MAGI adds back the same amount. A dependent's tax-exempt
        # interest, like the rest of the dependent's income, is not on it.
        interest = h["tax_exempt_interest"] + (
            h["spouse_tax_exempt_interest"] if h["joint"] else 0
        )
        bonds = (
            h["head_bonds"]
            + (h["spouse_bonds"] if h["joint"] else 0)
            + (h["dependent_bonds"] if h["has_dependent"] else 0)
        )
        if computed:
            # Wages include the possession and Puerto Rico income, which is
            # deducted again; AGI is the rest of the wages less the section
            # 135 exclusions, so the IRMAA MAGI does not depend on them.
            agi_without_135 = h["wages"] + (h["spouse_wages"] if h["joint"] else 0)
        else:
            agi_without_135 = h["agi"] + bonds
        expected = (
            agi_without_135
            + interest
            + section_911_excluded_income(h)
            + h["specified_possession_income"]
            + h["puerto_rico_income"]
        )
        assert magi[i] == pytest.approx(expected, abs=tolerance(expected)), (
            h,
            year,
            computed,
            magi[i],
        )


@hypothesis.settings(**SETTINGS)
@hypothesis.given(
    st.lists(irmaa_household_strategy, min_size=1, max_size=15),
    st.sampled_from(IRMAA_YEARS),
)
def test_irmaa_magi_adds_back_every_exclusion_to_a_provided_agi(households, year):
    assert_irmaa_identity(households, year, computed=False)


@hypothesis.settings(**SETTINGS)
@hypothesis.given(
    st.lists(irmaa_household_strategy, min_size=1, max_size=15),
    st.sampled_from(IRMAA_COMPUTED_YEARS),
)
def test_irmaa_magi_from_computed_agi_ignores_section_135(households, year):
    assert_irmaa_identity(households, year, computed=True)


# A parent with the section 135 exclusion recorded on a dependent student, and
# a joint couple with every exclusion and the Form 2555 amount above the
# stacking amount.
IRMAA_GRID = [
    dict(
        joint=False,
        has_dependent=True,
        agi=99_000,
        wages=100_000,
        spouse_wages=0,
        tax_exempt_interest=0,
        spouse_tax_exempt_interest=0,
        dependent_tax_exempt_interest=0,
        head_bonds=0,
        spouse_bonds=0,
        dependent_bonds=1_000,
        foreign_earned_income_exclusion=0,
        section_911_disallowed_deductions=0,
        set_section_911_amount=False,
        specified_possession_income=0,
        puerto_rico_income=0,
    ),
    dict(
        joint=True,
        has_dependent=True,
        agi=150_000,
        wages=120_000,
        spouse_wages=30_000,
        tax_exempt_interest=2_000,
        spouse_tax_exempt_interest=1_500,
        # The child's own; not on the parents' return.
        dependent_tax_exempt_interest=2_500,
        head_bonds=1_000,
        spouse_bonds=2_000,
        dependent_bonds=4_000,
        foreign_earned_income_exclusion=15_000,
        section_911_disallowed_deductions=10_000,
        set_section_911_amount=True,
        specified_possession_income=3_000,
        puerto_rico_income=4_000,
    ),
]


@pytest.mark.parametrize(
    "year, computed",
    [(year, False) for year in IRMAA_YEARS]
    + [(year, True) for year in IRMAA_COMPUTED_YEARS],
)
def test_irmaa_grid_keeps_the_identity(year, computed):
    assert_irmaa_identity(IRMAA_GRID, year, computed)
