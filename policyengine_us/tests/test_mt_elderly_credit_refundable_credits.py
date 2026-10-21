"""Property tests: refundable credits in the Montana elderly homeowner/renter
credit's gross household income.

ARM 42.4.301(2)(b)-(c) counts "federal refundable tax credits received" and
"any state refundable tax credits received" in gross household income, and
the 2024 Schedule 2EC line 8 combines "all the refundable credits received by
all household members". The model sums a person-level gross household income
over the household, so each tax unit's federal refundable credits are put on
its head once. These tests check that allocation for households of a claimant
aged 62 or older and a younger member who files their own return with up to
two children, so that the member can have a federal EITC and a refundable
child tax credit.

YAML cases cannot compare two simulations or draw household structures, so
this file does both. Each example runs the households twice: as given (W) and
with the federal refundable credits in gross household income set to zero
(Z). Properties, for every household:

1. Counted once: the household sum of the person-level federal credits
   equals the sum of income_tax_refundable_credits over its tax units, read
   from the tax-unit array.
2. Accounting: gross household income in W exceeds Z by exactly those
   credits.
3. More income never raises the credit: the credit in W is at most Z's.
4. The credit is between zero and the cap, and zero when gross household
   income is $45,000 or more.
5. Montana tax changes only through the credit: Montana refundable credits
   other than this one are the same in W and Z, and the household's Montana
   income tax rises by exactly the fall in its credit.

The model computes in single precision, so comparisons allow one cent or
eight float32 spacings at the amount compared, whichever is larger.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2024
CAP = 1_150
INCOME_LIMIT = 45_000
TOLERANCE = 0.01
FEDERAL = "mt_elderly_homeowner_or_renter_credit_federal_refundable_credits"
GROSS = "mt_elderly_homeowner_or_renter_credit_gross_household_income"
CREDIT = "mt_elderly_homeowner_or_renter_credit"


def build_situation(cases, zero_federal_credits):
    """One Montana household per case: the claimant files alone; the member
    files with their children. Also returns each person's and tax unit's
    case index."""
    people, tax_units, households, case_of = {}, {}, {}, {}
    for i, c in enumerate(cases):
        claimant, member = f"claimant_{i}", f"member_{i}"
        children = [f"child_{i}_{j}" for j in range(len(c["child_ages"]))]
        people[claimant] = {
            "age": {YEAR: c["claimant_age"]},
            "taxable_pension_income": {YEAR: c["pension"]},
            "real_estate_taxes": {YEAR: c["property_tax"]},
            "rent": {YEAR: c["rent"]},
        }
        people[member] = {
            "age": {YEAR: c["member_age"]},
            "employment_income": {YEAR: c["wages"]},
        }
        for child, age in zip(children, c["child_ages"]):
            people[child] = {"age": {YEAR: age}}
        tax_units[f"claimant_unit_{i}"] = {"members": [claimant]}
        tax_units[f"member_unit_{i}"] = {"members": [member, *children]}
        for name in [claimant, member, *children, *list(tax_units)[-2:]]:
            case_of[name] = i
        households[f"household_{i}"] = {
            "members": [claimant, member, *children],
            "state_code": {YEAR: "MT"},
        }
    if zero_federal_credits:
        # Set for everyone: an input for some people gives the others its
        # default, not its formula.
        for person in people.values():
            person[FEDERAL] = {YEAR: 0}
    situation = {"people": people, "tax_units": tax_units, "households": households}
    return situation, case_of


def calculate(cases, zero_federal_credits):
    """Household totals of person- and tax-unit-level variables, summed by
    entity id rather than array position."""
    situation, case_of = build_situation(cases, zero_federal_credits)
    simulation = Simulation(situation=situation)

    def by_household(variable, entity):
        values = np.asarray(simulation.calculate(variable, YEAR), dtype=float)
        totals = np.zeros(len(cases))
        for name, value in zip(simulation.populations[entity].ids, values):
            totals[case_of[name]] += value
        return totals

    return {
        "federal_person": by_household(FEDERAL, "person"),
        "federal_tax_unit": by_household("income_tax_refundable_credits", "tax_unit"),
        "gross": by_household(GROSS, "person"),
        "credit": by_household(CREDIT, "person"),
        "mt_other_credits": by_household(
            "mt_refundable_credits_before_renter_credit", "person"
        ),
        "mt_income_tax": by_household("mt_income_tax", "tax_unit"),
    }


def tolerance(amount):
    return max(TOLERANCE, 8 * float(np.spacing(np.float32(abs(amount)))))


def assert_properties(cases):
    w = calculate(cases, zero_federal_credits=False)
    z = calculate(cases, zero_federal_credits=True)
    for i, c in enumerate(cases):
        tol = tolerance(w["gross"][i])
        federal = w["federal_tax_unit"][i]
        # 1. Each tax unit's federal refundable credits count once.
        assert w["federal_person"][i] == pytest.approx(federal, abs=tol), c
        assert z["federal_person"][i] == 0, c
        # 2. They are the whole difference in gross household income.
        assert w["gross"][i] - z["gross"][i] == pytest.approx(federal, abs=tol), c
        # 3. More income never raises the credit.
        assert w["credit"][i] <= z["credit"][i] + tol, c
        for result in (w, z):
            # 4. Bounds and the income limit.
            assert -tol <= result["credit"][i] <= CAP + tol, c
            if result["gross"][i] >= INCOME_LIMIT + tol:
                assert result["credit"][i] == 0, c
        # 5. Montana tax moves only through this credit.
        assert w["mt_other_credits"][i] == pytest.approx(
            z["mt_other_credits"][i], abs=TOLERANCE
        ), c
        assert w["mt_income_tax"][i] - z["mt_income_tax"][i] == pytest.approx(
            z["credit"][i] - w["credit"][i], abs=tolerance(z["credit"][i])
        ), c


def test_worked_example():
    """2024 Schedule 2EC: the claimant's line 5 pension 20,000; the
    daughter's wages 10,000 (line 17) and her line 8 credits: federal EITC
    34% x 10,000 = 3,400, refundable child tax credit min(1,700, 15% x
    7,500) = 1,125 and Montana EITC 340. Line 18 = 34,865; line 22 =
    (34,865 - 12,600) x 0.05 = 1,113.25; line 27 = 2,000 - 1,113.25 =
    886.75; line 30 = 886.75. Without the federal credits, line 18 =
    30,340, line 22 = 887 and line 30 = 1,113."""
    case = {
        "claimant_age": 70,
        "pension": 20_000,
        "property_tax": 2_000,
        "rent": 0,
        "member_age": 30,
        "wages": 10_000,
        "child_ages": [5],
    }
    w = calculate([case], zero_federal_credits=False)
    z = calculate([case], zero_federal_credits=True)
    assert w["federal_tax_unit"][0] == pytest.approx(4_525, abs=TOLERANCE)
    assert w["gross"][0] == pytest.approx(34_865, abs=TOLERANCE)
    assert w["credit"][0] == pytest.approx(886.75, abs=TOLERANCE)
    assert z["gross"][0] == pytest.approx(30_340, abs=TOLERANCE)
    assert z["credit"][0] == pytest.approx(1_113, abs=TOLERANCE)
    assert_properties([case])


try:
    import hypothesis
    import hypothesis.strategies as st
except ImportError:  # pragma: no cover
    hypothesis = None

if hypothesis is not None:
    # Each example builds two Simulations; on a loaded runner input
    # generation can trip the too_slow health check, which says nothing about
    # the model.
    SLOW = [hypothesis.HealthCheck.too_slow]

    def amount(high):
        return st.one_of(st.just(0), st.integers(min_value=1, max_value=high))

    @st.composite
    def case(draw):
        return {
            "claimant_age": draw(st.integers(min_value=62, max_value=90)),
            "pension": draw(amount(40_000)),
            "property_tax": draw(st.integers(min_value=0, max_value=4_000)),
            "rent": draw(amount(12_000)),
            "member_age": draw(st.integers(min_value=19, max_value=61)),
            "wages": draw(amount(30_000)),
            "child_ages": draw(
                st.lists(st.integers(min_value=0, max_value=16), max_size=2)
            ),
        }

    @hypothesis.settings(max_examples=10, deadline=None, suppress_health_check=SLOW)
    @hypothesis.given(st.lists(case(), min_size=1, max_size=6))
    def test_properties(cases):
        assert_properties(cases)
