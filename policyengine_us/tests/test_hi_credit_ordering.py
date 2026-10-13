"""Property tests: Hawaii applies refundable credits before nonrefundable ones.

Form N-11, lines 27 to 36, in every year from 2018 to 2025:

- line 33 totals the refundable credits claimed on the return;
- line 34, the adjusted tax liability, is line 27 (tax) minus line 33;
- line 35 totals the nonrefundable credits, and the instructions say "the
  total of the nonrefundable credits used cannot be greater than your
  adjusted tax liability. If line 34 is zero or less, nonrefundable tax
  credits may not be used";
- line 36 is line 34 minus line 35.

Form N-356, lines 10 to 13, limits the 2018 to 2022 nonrefundable earned
income tax credit (20% of the federal credit) to line 34. The Act 115 refund
of 2021 was issued apart from the return, so it is not on line 33.

A reference written from those lines is compared with the model. For tax T,
refundable credits R (of which the Act 115 refund is A in 2021), and a
nonrefundable potential N (the earned income tax credit while it is
nonrefundable, zero from 2023):

1. hi_adjusted_tax_liability = T - (R - A).
2. hi_non_refundable_credits = min(N, max(T - (R - A), 0)).
3. hi_income_tax = line 36 - A, and also equals
   hi_income_tax_before_refundable_credits - hi_refundable_credits, the
   identity the household-level state lists rely on.
4. Refundable credits are paid in full: when R - A >= T, no nonrefundable
   credit applies and hi_income_tax = T - R.
5. min(T - R, -A) <= hi_income_tax <= T - R.
6. Raising R by d lowers hi_income_tax by between 0 and d, and raising the
   federal earned income tax credit never raises it.

The model computes in single precision, so comparisons allow one cent or
eight float32 spacings at the largest amount, whichever is larger.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
# Years in which the Hawaii earned income tax credit is nonrefundable and the
# Act 115 refund is paid.
NON_REFUNDABLE_EITC_YEARS = range(2018, 2023)
ACT_115_YEAR = 2021
EITC_MATCH = 0.2
MAX_AMOUNT = 20_000

OUTPUTS = [
    "hi_adjusted_tax_liability",
    "hi_non_refundable_credits",
    "hi_income_tax_before_refundable_credits",
    "hi_income_tax",
    "state_income_tax",
    "state_non_refundable_credits",
]


def tolerance(*amounts):
    scale = np.float32(max(np.max(np.abs(a)) for a in amounts))
    return max(0.01, 8 * float(np.spacing(scale)))


def act_115_paid(unit, year):
    return unit["act_115"] if year == ACT_115_YEAR else 0


def calculate(units, year):
    """One Hawaii tax unit per household. Each unit sets its tax, refundable
    credits, Act 115 refund and federal earned income tax credit."""
    people, tax_units, households = {}, {}, {}
    for i, unit in enumerate(units):
        people[f"p{i}"] = {"age": {year: 30}}
        tax_units[f"t{i}"] = {
            "members": [f"p{i}"],
            "hi_income_tax_before_non_refundable_credits": {year: unit["tax"]},
            "hi_refundable_credits": {year: unit["refundable"]},
            # The refund is paid only in 2021; a zero refund in other years
            # keeps the reference to the law whatever the parameters list.
            "hi_act_115_rebate": {year: act_115_paid(unit, year)},
            "eitc": {year: unit["eitc"]},
        }
        households[f"h{i}"] = {"members": [f"p{i}"], "state_code": {year: "HI"}}
    sim = Simulation(
        situation={"people": people, "tax_units": tax_units, "households": households}
    )
    return {name: sim.calculate(name, year) for name in OUTPUTS}


def reference(units, year):
    tax = np.array([u["tax"] for u in units], dtype=float)
    refundable = np.array([u["refundable"] for u in units], dtype=float)
    act_115 = np.array([act_115_paid(u, year) for u in units], dtype=float)
    eitc = np.array([u["eitc"] for u in units], dtype=float)
    potential = EITC_MATCH * eitc if year in NON_REFUNDABLE_EITC_YEARS else 0 * eitc
    line_34 = tax - (refundable - act_115)
    line_35 = np.minimum(potential, np.maximum(line_34, 0))
    return tax, refundable, act_115, line_34, line_35


def check(units, year):
    result = calculate(units, year)
    tax, refundable, act_115, line_34, line_35 = reference(units, year)
    tol = tolerance(tax, refundable, line_34)
    income_tax = result["hi_income_tax"]
    # 1. Line 34.
    np.testing.assert_allclose(result["hi_adjusted_tax_liability"], line_34, atol=tol)
    # 2. Line 35.
    np.testing.assert_allclose(result["hi_non_refundable_credits"], line_35, atol=tol)
    # 3. Line 36, less the Act 115 refund. This also shows that the floor in
    # hi_income_tax_before_refundable_credits never binds.
    np.testing.assert_allclose(income_tax, line_34 - line_35 - act_115, atol=tol)
    # The identities the household-level lists rely on. They hold by the
    # current definitions of hi_income_tax and state_income_tax; these
    # guard them against a later change to either.
    np.testing.assert_allclose(
        income_tax,
        result["hi_income_tax_before_refundable_credits"] - refundable,
        atol=tol,
    )
    np.testing.assert_allclose(result["state_income_tax"], income_tax, atol=tol)
    np.testing.assert_allclose(
        result["state_non_refundable_credits"],
        result["hi_non_refundable_credits"],
        atol=tol,
    )
    # 4. Refundable credits are paid in full.
    covered = line_34 <= 0
    assert (result["hi_non_refundable_credits"][covered] <= tol).all()
    np.testing.assert_allclose(
        income_tax[covered], (tax - refundable)[covered], atol=tol
    )
    # 5. Bounds.
    assert (income_tax <= tax - refundable + tol).all()
    assert (income_tax >= np.minimum(tax - refundable, -act_115) - tol).all()
    return result


def check_monotonic(units, year, refundable_step, eitc_step):
    """6. A second copy of every unit with more refundable credits, and a
    third with a larger federal earned income tax credit."""
    more_refundable = [
        {**u, "refundable": u["refundable"] + refundable_step} for u in units
    ]
    more_eitc = [{**u, "eitc": u["eitc"] + eitc_step} for u in units]
    result = check(units + more_refundable + more_eitc, year)
    n = len(units)
    income_tax = result["hi_income_tax"]
    base, raised_r, raised_e = (
        income_tax[:n],
        income_tax[n : 2 * n],
        income_tax[2 * n :],
    )
    tol = tolerance(income_tax)
    change = base - raised_r
    assert (change >= -tol).all()
    assert (change <= refundable_step + tol).all()
    assert (raised_e <= base + tol).all()


amount = st.one_of(st.just(0), st.integers(1, MAX_AMOUNT))
unit_strategy = st.builds(
    lambda tax, refundable, act_115_share, eitc: {
        "tax": tax,
        "refundable": refundable,
        # The Act 115 refund is part of the refundable credits.
        "act_115": act_115_share * refundable // 100,
        "eitc": eitc,
    },
    amount,
    amount,
    st.integers(0, 100),
    amount,
)

# Boundaries: no tax, tax equal to the refundable credits, tax equal to the
# refundable credits plus the nonrefundable credit, and either side of each.
GRID = [
    {"tax": tax, "refundable": refundable, "act_115": act_115, "eitc": eitc}
    for refundable in (0, 300, 1_000)
    for act_115 in sorted({0, refundable // 3})
    for eitc in (0, 2_500)
    for tax in sorted(
        {
            0,
            max(refundable - act_115 - 1, 0),
            refundable - act_115,
            refundable - act_115 + 1,
            refundable - act_115 + 250,
            refundable - act_115 + 500,
            refundable - act_115 + 501,
            5_000,
        }
    )
]


@pytest.mark.parametrize("year", YEARS)
def test_grid_follows_form_n11(year):
    check_monotonic(GRID, year, refundable_step=200, eitc_step=1_000)


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    st.lists(unit_strategy, min_size=1, max_size=20),
    st.sampled_from(YEARS),
    st.integers(1, 2_000),
    st.integers(1, 5_000),
)
def test_random_units_follow_form_n11(units, year, refundable_step, eitc_step):
    check_monotonic(units, year, refundable_step, eitc_step)


def test_grid_binds_each_case():
    # The 2022 grid has units with line 34 at or below zero, units whose
    # nonrefundable credit is cut to line 34, and units that use it in full.
    _, _, _, line_34, line_35 = reference(GRID, 2022)
    potential = EITC_MATCH * np.array([u["eitc"] for u in GRID])
    assert (line_34 <= 0).any()
    assert ((line_35 > 0) & (line_35 < potential)).any()
    assert ((line_35 > 0) & (line_35 == potential)).any()


def calculate_households(households, year):
    """Hawaii households whose credits the model computes: a head (and a
    spouse) with wages and rent, and children aged 5."""
    people, tax_units, households_out = {}, {}, {}
    for i, h in enumerate(households):
        members = [f"head{i}"]
        people[f"head{i}"] = {
            "age": {year: 30},
            "employment_income": {year: h["wages"]},
            "rent": {year: h["rent"]},
        }
        if h["married"]:
            members.append(f"spouse{i}")
            people[f"spouse{i}"] = {
                "age": {year: 30},
                "employment_income": {year: h["spouse_wages"]},
            }
        for c in range(h["children"]):
            members.append(f"child{i}_{c}")
            people[f"child{i}_{c}"] = {"age": {year: 5}}
        tax_units[f"t{i}"] = {"members": members}
        households_out[f"h{i}"] = {"members": members, "state_code": {year: "HI"}}
    sim = Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households_out,
        }
    )
    names = OUTPUTS + [
        "hi_income_tax_before_non_refundable_credits",
        "hi_refundable_credits",
        "hi_act_115_rebate",
        "hi_eitc_potential",
    ]
    return {name: sim.calculate(name, year) for name in names}


household_strategy = st.fixed_dictionaries(
    {
        "married": st.booleans(),
        "children": st.integers(0, 3),
        "wages": st.one_of(st.just(0), st.integers(1, 60_000)),
        "spouse_wages": st.one_of(st.just(0), st.integers(1, 30_000)),
        "rent": st.one_of(st.just(0), st.integers(1, 24_000)),
    }
)


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    st.lists(household_strategy, min_size=1, max_size=20),
    st.sampled_from([2021, 2022, 2025]),
)
def test_computed_credits_follow_form_n11(households, year):
    # Properties 1 to 3 with the tax and credits the model computes.
    r = calculate_households(households, year)
    tax = r["hi_income_tax_before_non_refundable_credits"]
    refundable = r["hi_refundable_credits"]
    act_115 = r["hi_act_115_rebate"] if year == ACT_115_YEAR else 0 * tax
    potential = r["hi_eitc_potential"] if year in NON_REFUNDABLE_EITC_YEARS else 0 * tax
    line_34 = tax - (refundable - act_115)
    line_35 = np.minimum(potential, np.maximum(line_34, 0))
    tol = tolerance(tax, refundable)
    np.testing.assert_allclose(r["hi_adjusted_tax_liability"], line_34, atol=tol)
    np.testing.assert_allclose(r["hi_non_refundable_credits"], line_35, atol=tol)
    np.testing.assert_allclose(
        r["hi_income_tax"], line_34 - line_35 - act_115, atol=tol
    )
    np.testing.assert_allclose(r["state_income_tax"], r["hi_income_tax"], atol=tol)


def test_credit_lists_do_not_overlap():
    # A credit in both lists would make hi_non_refundable_credits depend on
    # itself through line 34 (hi_adjusted_tax_liability).
    from policyengine_us.system import system

    for year in range(2015, 2036):
        credits = system.parameters(f"{year}-01-01").gov.states.hi.tax.income.credits
        overlap = set(credits.refundable) & set(credits.non_refundable)
        assert not overlap, (year, overlap)


@pytest.mark.parametrize("year", [2021, 2022])
def test_computed_wage_ladder_reaches_the_line_34_limit(year):
    # Single filers and married filers with two children, $0 to $40,000 of
    # wages in $500 steps: low earners have refundable credits above the tax,
    # then the nonrefundable credit is cut to line 34, then used in full.
    households = [
        {
            "married": married,
            "children": 2 if married else 0,
            "wages": wages,
            "spouse_wages": 0,
            "rent": 0,
        }
        for married in (False, True)
        for wages in range(0, 40_001, 500)
    ]
    r = calculate_households(households, year)
    tax = r["hi_income_tax_before_non_refundable_credits"]
    refundable = r["hi_refundable_credits"]
    act_115 = r["hi_act_115_rebate"] if year == ACT_115_YEAR else 0 * tax
    potential = r["hi_eitc_potential"]
    line_34 = tax - (refundable - act_115)
    line_35 = np.minimum(potential, np.maximum(line_34, 0))
    tol = tolerance(tax, refundable)
    np.testing.assert_allclose(r["hi_non_refundable_credits"], line_35, atol=tol)
    np.testing.assert_allclose(
        r["hi_income_tax"], line_34 - line_35 - act_115, atol=tol
    )
    applies = potential > 0
    assert (applies & (line_34 <= 0)).any()
    assert (applies & (line_34 > 0) & (line_35 < potential - tol)).any()
    assert (applies & (line_35 >= potential - tol)).any()
