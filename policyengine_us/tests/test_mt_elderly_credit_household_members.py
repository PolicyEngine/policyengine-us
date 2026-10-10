"""Property tests: household members' income in the Montana elderly
homeowner/renter credit.

MCA 15-30-2337(4) defines gross household income as "all income received by
all individuals of a household while they are members of the household", and
(9)(a) counts federal adjusted gross income "without regard to loss" plus
nontaxable income, including all Social Security. The 2024 Schedule 2EC lists
the claimant's income by category (line 7: "do not include any capital
losses"; line 6: "the total taxable and nontaxable Social Security benefits")
and puts the income of "other members of your household" on line 17.

The model reaches the same quantity by two paths. A member who is the
claimant's tax unit dependent is counted through dependent_gross_income and
dependent_taxable_social_security; a member who files their own return is
counted through federal AGI, the loss add-back and taxable_social_security.
For a claimant aged 62 or older (taxable pension, Social Security, property
tax, rent) and one other adult in the household (taxable interest, a
long-term capital gain or loss, Social Security):

1. The household's gross household income is the claimant's pension and
   Social Security plus the other member's interest, positive capital gain
   and Social Security, whichever path counts the other member.
2. So the claimant's credit is the same in both arrangements, and the other
   member's own tax unit, with no one aged 62 or older, claims nothing.
3. The credit is between zero and the cap, and zero when gross household
   income is $45,000 or more (line 29).
4. More interest for the other member never raises the credit: gross
   household income rises, so net household income (line 22) cannot fall
   and the credit multiplier (line 29) cannot rise.

No one has earned income, so no refundable credit enters line 8. The model
computes in single precision, so comparisons allow one cent or eight float32
spacings at the household's total income, whichever is larger.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2024
CAP = 1_150
INCOME_LIMIT = 45_000
TOLERANCE = 0.01


def build_situation(cases):
    """Three Montana households per case: (A) the other member is the
    claimant's dependent, (B) the other member files their own return and
    (C) as A with the other member's extra interest added."""
    people, tax_units, marital_units, spm_units, families, households = (
        {},
        {},
        {},
        {},
        {},
        {},
    )
    for i, c in enumerate(cases):
        for arrangement in "ABC":
            key = f"{arrangement}{i}"
            claimant, member = f"claimant_{key}", f"member_{key}"
            interest = c["interest"] + (
                c["extra_interest"] if arrangement == "C" else 0
            )
            people[claimant] = {
                "age": {YEAR: c["claimant_age"]},
                "taxable_pension_income": {YEAR: c["pension"]},
                "social_security_retirement": {YEAR: c["claimant_ss"]},
                "real_estate_taxes": {YEAR: c["property_tax"]},
                "rent": {YEAR: c["rent"]},
            }
            people[member] = {
                "age": {YEAR: c["member_age"]},
                "taxable_interest_income": {YEAR: interest},
                "long_term_capital_gains": {YEAR: c["capital_gain"]},
                "social_security_survivors": {YEAR: c["member_ss"]},
            }
            if arrangement == "B":
                tax_units[f"tax_unit_{key}"] = {"members": [claimant]}
                tax_units[f"tax_unit_{key}_member"] = {"members": [member]}
            else:
                tax_units[f"tax_unit_{key}"] = {"members": [claimant, member]}
            # Set for everyone: an input for some people gives the others
            # its default (false), not its formula. Without it the model
            # takes an adult in the claimant's tax unit to be the spouse.
            people[claimant]["is_tax_unit_dependent"] = {YEAR: False}
            people[member]["is_tax_unit_dependent"] = {YEAR: arrangement != "B"}
            marital_units[f"marital_unit_{key}"] = {"members": [claimant]}
            marital_units[f"marital_unit_{key}_member"] = {"members": [member]}
            spm_units[f"spm_unit_{key}"] = {"members": [claimant, member]}
            families[f"family_{key}"] = {"members": [claimant, member]}
            households[f"household_{key}"] = {
                "members": [claimant, member],
                "state_code": {YEAR: "MT"},
            }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "spm_units": spm_units,
        "families": families,
        "households": households,
    }


def calculate(cases):
    """Household totals of gross household income and the credit, and the
    other member's credit, as arrays indexed [arrangement, case]."""
    simulation = Simulation(situation=build_situation(cases))
    gross_household_income = np.asarray(
        simulation.calculate(
            "mt_elderly_homeowner_or_renter_credit_gross_household_income",
            YEAR,
            map_to="household",
        )
    )
    credit = np.asarray(
        simulation.calculate(
            "mt_elderly_homeowner_or_renter_credit", YEAR, map_to="household"
        )
    )
    person_credit = np.asarray(
        simulation.calculate("mt_elderly_homeowner_or_renter_credit", YEAR)
    )
    dependent = np.asarray(simulation.calculate("is_tax_unit_dependent", YEAR))
    # Households and people are in situation order: A0, B0, C0, A1, ...;
    # the member follows the claimant.
    n = len(cases)
    return {
        "gross_household_income": gross_household_income.reshape(n, 3).T,
        "credit": credit.reshape(n, 3).T,
        "member_credit": person_credit[1::2].reshape(n, 3).T,
        "member_is_dependent": dependent[1::2].reshape(n, 3).T,
    }


def expected_gross_household_income(c, extra_interest=0):
    """2024 Schedule 2EC line 18: lines 5 and 6 for the claimant, and line
    17 for the other member's interest, gains and Social Security."""
    claimant = c["pension"] + c["claimant_ss"]
    member = c["interest"] + extra_interest + max(0, c["capital_gain"])
    return claimant + member + c["member_ss"]


def tolerance(amount):
    return max(TOLERANCE, 8 * float(np.spacing(np.float32(abs(amount)))))


def assert_properties(cases):
    result = calculate(cases)
    a, b, c_ = 0, 1, 2
    # The other member is a dependent in A and C and their own filer in B.
    assert result["member_is_dependent"].tolist() == [
        [True] * len(cases),
        [False] * len(cases),
        [True] * len(cases),
    ]
    for i, c in enumerate(cases):
        expected = expected_gross_household_income(c)
        tol = tolerance(expected + c["extra_interest"])
        ghi = result["gross_household_income"]
        credit = result["credit"]
        # 1. Both paths give the Schedule 2EC total.
        assert ghi[a, i] == pytest.approx(expected, abs=tol), c
        assert ghi[b, i] == pytest.approx(expected, abs=tol), c
        assert ghi[c_, i] == pytest.approx(expected + c["extra_interest"], abs=tol), c
        # 2. The claimant's credit does not depend on the arrangement, and
        # the other member claims nothing.
        assert credit[a, i] == pytest.approx(credit[b, i], abs=tol), c
        assert np.all(result["member_credit"][:, i] == 0), c
        for arrangement in (a, b, c_):
            # 3. Bounds and the income limit.
            assert -tol <= credit[arrangement, i] <= CAP + tol, c
            if ghi[arrangement, i] >= INCOME_LIMIT + tol:
                assert credit[arrangement, i] == 0, c
        # 4. More income never raises the credit.
        assert credit[c_, i] <= credit[a, i] + tol, c


def test_worked_example():
    """2024 Schedule 2EC: line 5 pension 20,000; line 17 the other member's
    interest 10,000; line 18 = 30,000; line 22 = (30,000 - 12,600) x 0.05 =
    870; line 27 = 2,000 - 870 = 1,130; line 30 = 1,130 in both
    arrangements. With 5,000 more interest, line 18 = 35,000; line 22 =
    1,120; line 28 = 880; line 29 = 40%; line 30 = 352."""
    case = {
        "claimant_age": 70,
        "pension": 20_000,
        "claimant_ss": 0,
        "property_tax": 2_000,
        "rent": 0,
        "member_age": 40,
        "interest": 10_000,
        "capital_gain": 0,
        "member_ss": 0,
        "extra_interest": 5_000,
    }
    result = calculate([case])
    assert result["gross_household_income"][:, 0] == pytest.approx(
        [30_000, 30_000, 35_000], abs=TOLERANCE
    )
    assert result["credit"][:, 0] == pytest.approx([1_130, 1_130, 352], abs=TOLERANCE)
    assert_properties([case])


try:
    import hypothesis
    import hypothesis.strategies as st
except ImportError:  # pragma: no cover
    hypothesis = None

if hypothesis is not None:
    # Each example builds a Simulation; on a loaded runner input generation
    # can trip the too_slow health check, which says nothing about the model.
    SLOW = [hypothesis.HealthCheck.too_slow]

    def amount(high):
        return st.one_of(st.just(0), st.integers(min_value=1, max_value=high))

    @st.composite
    def case(draw):
        return {
            "claimant_age": draw(st.integers(min_value=62, max_value=90)),
            "pension": draw(amount(40_000)),
            "claimant_ss": draw(amount(30_000)),
            "property_tax": draw(st.integers(min_value=0, max_value=4_000)),
            "rent": draw(amount(12_000)),
            "member_age": draw(st.integers(min_value=15, max_value=61)),
            "interest": draw(amount(40_000)),
            "capital_gain": draw(
                st.one_of(st.just(0), st.integers(min_value=-20_000, max_value=40_000))
            ),
            "member_ss": draw(amount(20_000)),
            "extra_interest": draw(st.integers(min_value=1, max_value=20_000)),
        }

    @hypothesis.settings(max_examples=15, deadline=None, suppress_health_check=SLOW)
    @hypothesis.given(st.lists(case(), min_size=1, max_size=8))
    def test_properties(cases):
        assert_properties(cases)
