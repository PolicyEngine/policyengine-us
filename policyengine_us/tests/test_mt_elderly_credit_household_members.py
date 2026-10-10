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
claimant's tax unit dependent is counted through their income and permitted
adjustments; a member who files their own return is counted through federal
AGI, the loss add-back and taxable_social_security.
For a claimant aged 62 or older (taxable pension, Social Security, property
tax, rent) and one other member in the household (taxable interest, a
long-term capital gain or loss, Social Security, self-employment profit and
permitted non-loss adjustments):

1. The household's gross household income is the claimant's pension and
   Social Security plus the other member's interest, positive capital gain,
   self-employment profit and Social Security, less permitted non-loss
   adjustments, whichever path counts the other member. Capital losses
   cannot reduce this amount.
2. So the claimant's credit is the same in both arrangements, and the other
   member's own tax unit, with no one aged 62 or older, claims nothing.
3. The credit is between zero and the cap, and zero when gross household
   income is $45,000 or more (line 29).
4. More interest for the other member never raises the credit: gross
   household income rises, so net household income (line 22) cannot fall
   and the credit multiplier (line 29) cannot rise.
5. Early-withdrawal penalties and self-employed health/pension expenses
   reduce household income by their deductible amounts, even when those
   adjustments make the member's contribution negative.

Earned-income cases keep the other member under 25 with no dependents on
their own return, so neither arrangement receives refundable earned-income
or child tax credits. The claimant has no earned income. The model computes
in single precision, so comparisons allow one cent or eight float32 spacings
at the household's total income, whichever is larger.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2024
CAP = 1_150
INCOME_LIMIT = 45_000
TOLERANCE = 0.01
ARRANGEMENTS = "ABCD"


def build_situation(cases):
    """Four Montana households per case: (A) the other member is the
    claimant's dependent, (B) the other member files their own return and
    (C) as A with the other member's extra interest added, and (D) as A
    without early-withdrawal, self-employed health or pension expenses."""
    people, tax_units, marital_units, spm_units, families, households = (
        {},
        {},
        {},
        {},
        {},
        {},
    )
    for i, c in enumerate(cases):
        for arrangement in ARRANGEMENTS:
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
                "self_employment_income": {YEAR: c["self_employment_income"]},
                "early_withdrawal_penalty": {
                    YEAR: 0 if arrangement == "D" else c["early_withdrawal_penalty"]
                },
                "self_employed_health_insurance_premiums": {
                    YEAR: 0 if arrangement == "D" else c["health_premiums"]
                },
                "self_employed_pension_contributions": {
                    YEAR: 0 if arrangement == "D" else c["pension_contributions"]
                },
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
    other_refundable_credits = np.asarray(
        simulation.calculate(
            "mt_refundable_credits_before_renter_credit", YEAR, map_to="household"
        )
    )
    # Households and people are in situation order: A0, B0, C0, D0, A1, ...;
    # the member follows the claimant.
    n, arrangements = len(cases), len(ARRANGEMENTS)
    return {
        "gross_household_income": gross_household_income.reshape(n, arrangements).T,
        "credit": credit.reshape(n, arrangements).T,
        "member_credit": person_credit[1::2].reshape(n, arrangements).T,
        "member_is_dependent": dependent[1::2].reshape(n, arrangements).T,
        "other_refundable_credits": other_refundable_credits.reshape(n, arrangements).T,
    }


def elective_adjustments(c):
    # Generated health premiums and pension contributions stay below the
    # member's eligible self-employment earnings, so all are deductible.
    return (
        c["early_withdrawal_penalty"]
        + c["health_premiums"]
        + c["pension_contributions"]
    )


def expected_gross_household_income(c):
    """All members' federal AGI without losses, plus nontaxable income:
    MCA 15-30-2337(9); 2023 Form 2 instructions PDF pp. 51-52.
    https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=51
    """
    claimant = c["pension"] + c["claimant_ss"]
    member = c["interest"] + max(0, c["capital_gain"]) + c["self_employment_income"]
    # Schedule SE lines 4a, 4c, 10-13: taxable earnings are 92.35% of
    # profit; no SE tax below $400. Generated profits stay below the
    # Social Security wage base, and no one has wages.
    # https://www.irs.gov/pub/irs-prior/f1040sse--2024.pdf#page=1
    taxable_earnings = c["self_employment_income"] * 0.9235
    half_se_tax = (
        taxable_earnings * (0.124 + 0.029) * 0.5 if taxable_earnings >= 400 else 0
    )
    member -= half_se_tax + elective_adjustments(c)
    return claimant + member + c["member_ss"]


def tolerance(amount):
    return max(TOLERANCE, 8 * float(np.spacing(np.float32(abs(amount)))))


def assert_properties(cases):
    result = calculate(cases)
    a, b, c_, d = 0, 1, 2, 3
    # Equivalence assumes these income definitions contain no refundable
    # credits whose eligibility changes when the member files separately.
    assert np.all(result["other_refundable_credits"] == 0), cases
    # The other member is a dependent in A, C and D and their own filer in B.
    assert result["member_is_dependent"].tolist() == [
        [True] * len(cases),
        [False] * len(cases),
        [True] * len(cases),
        [True] * len(cases),
    ]
    for i, c in enumerate(cases):
        expected = expected_gross_household_income(c)
        expenses = elective_adjustments(c)
        tol = tolerance(expected + c["extra_interest"] + expenses)
        ghi = result["gross_household_income"]
        credit = result["credit"]
        # 1. Both paths give the Schedule 2EC total.
        assert ghi[a, i] == pytest.approx(expected, abs=tol), c
        assert ghi[b, i] == pytest.approx(expected, abs=tol), c
        assert ghi[c_, i] == pytest.approx(expected + c["extra_interest"], abs=tol), c
        assert ghi[d, i] == pytest.approx(expected + expenses, abs=tol), c
        # 2. The claimant's credit does not depend on the arrangement, and
        # the other member claims nothing.
        assert credit[a, i] == pytest.approx(credit[b, i], abs=tol), c
        assert np.all(result["member_credit"][:, i] == 0), c
        for arrangement in (a, b, c_, d):
            # 3. Bounds and the income limit.
            assert -tol <= credit[arrangement, i] <= CAP + tol, c
            if ghi[arrangement, i] >= INCOME_LIMIT + tol:
                assert credit[arrangement, i] == 0, c
        # 4. More income never raises the credit.
        assert credit[c_, i] <= credit[a, i] + tol, c
        # 5. Non-loss adjustments lower income by the full deductible
        # amount, including when the member has negative AGI without losses.
        assert ghi[d, i] - ghi[a, i] == pytest.approx(expenses, abs=tol), c
        assert credit[d, i] <= credit[a, i] + tol, c


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
        "self_employment_income": 0,
        "early_withdrawal_penalty": 0,
        "health_premiums": 0,
        "pension_contributions": 0,
        "extra_interest": 5_000,
    }
    result = calculate([case])
    assert result["gross_household_income"][:, 0] == pytest.approx(
        [30_000, 30_000, 35_000, 30_000], abs=TOLERANCE
    )
    assert result["credit"][:, 0] == pytest.approx(
        [1_130, 1_130, 352, 1_130], abs=TOLERANCE
    )
    assert_properties([case])


def negative_household_cases():
    return [
        {
            "claimant_age": claimant_age,
            "pension": 0,
            "claimant_ss": 347,
            "property_tax": 319,
            "rent": 0,
            "member_age": 43,
            "interest": interest,
            "capital_gain": 0,
            "member_ss": member_ss,
            "self_employment_income": 0,
            "early_withdrawal_penalty": penalty,
            "health_premiums": 0,
            "pension_contributions": 0,
            "extra_interest": extra_interest,
        }
        for claimant_age, interest, member_ss, penalty, extra_interest in (
            (62, 4_420, 894, 5_986, 377),
            (86, 0, 0, 894, 1),
        )
    ]


def test_negative_household_income_keeps_full_multiplier():
    # 347 + 4,420 + 894 - 5,986 = -325; adding 377 gives 52;
    # removing the penalty gives 5,661. In the second case, 347 - 894
    # = -547, or -546 with extra interest, or 347 without the penalty.
    # Every total is below 12,600, so net household contribution is zero.
    # Line 29 gives 100% below 35,000, so the 319 property tax is paid:
    # https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=49
    result = calculate(negative_household_cases())
    assert result["gross_household_income"] == pytest.approx(
        np.array([[-325, -547], [-325, -547], [52, -546], [5_661, 347]]),
        abs=TOLERANCE,
    )
    assert result["credit"] == pytest.approx(np.full((4, 2), 319), abs=TOLERANCE)


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
        if high == 0:
            return st.just(0)
        return st.one_of(st.just(0), st.integers(min_value=1, max_value=high))

    @st.composite
    def case(draw):
        member_age = draw(st.integers(min_value=15, max_value=61))
        self_employment_income = draw(amount(20_000)) if member_age <= 24 else 0
        return {
            "claimant_age": draw(st.integers(min_value=62, max_value=90)),
            "pension": draw(amount(40_000)),
            "claimant_ss": draw(amount(30_000)),
            "property_tax": draw(st.integers(min_value=0, max_value=4_000)),
            "rent": draw(amount(12_000)),
            "member_age": member_age,
            "interest": draw(amount(40_000)),
            "capital_gain": draw(
                st.one_of(st.just(0), st.integers(min_value=-20_000, max_value=40_000))
            ),
            "member_ss": draw(amount(20_000)),
            "self_employment_income": self_employment_income,
            "early_withdrawal_penalty": draw(amount(40_000)),
            # Keep these expenses within earned income and conservative
            # plan limits, so both filer arrangements permit the deduction.
            "health_premiums": draw(amount(self_employment_income // 4)),
            "pension_contributions": draw(amount(self_employment_income // 10)),
            "extra_interest": draw(st.integers(min_value=1, max_value=20_000)),
        }

    @hypothesis.settings(
        max_examples=15, derandomize=True, deadline=None, suppress_health_check=SLOW
    )
    @hypothesis.example(negative_household_cases())
    @hypothesis.example(
        [
            # P2: 10,000 * .9235 * .153 / 2 = 706.4775;
            # gross household income = 20,000 + 10,000 - 706.4775.
            {
                "claimant_age": 70,
                "pension": 20_000,
                "claimant_ss": 0,
                "property_tax": 0,
                "rent": 12_000,
                "member_age": 18,
                "interest": 0,
                "capital_gain": 0,
                "member_ss": 0,
                "self_employment_income": 10_000,
                "early_withdrawal_penalty": 0,
                "health_premiums": 0,
                "pension_contributions": 0,
                "extra_interest": 1_000,
            },
            # The capital loss is excluded. 3,000 * .9235 * .153 / 2
            # = 211.94325; the other adjustments total 5,700, leaving
            # member income 3,500 - 211.94325 - 5,700 = -2,411.94325.
            {
                "claimant_age": 70,
                "pension": 20_000,
                "claimant_ss": 0,
                "property_tax": 0,
                "rent": 12_000,
                "member_age": 24,
                "interest": 500,
                "capital_gain": -3_000,
                "member_ss": 0,
                "self_employment_income": 3_000,
                "early_withdrawal_penalty": 5_000,
                "health_premiums": 500,
                "pension_contributions": 200,
                "extra_interest": 1_000,
            },
        ]
    )
    @hypothesis.example(
        [
            # Taxable SE earnings: 433 * .9235 = 399.8755 (no tax),
            # 434 * .9235 = 400.799 (half-tax deduction 30.6611235).
            {
                "claimant_age": 70,
                "pension": 20_000,
                "claimant_ss": 0,
                "property_tax": 0,
                "rent": 12_000,
                "member_age": 18,
                "interest": 0,
                "capital_gain": 0,
                "member_ss": 0,
                "self_employment_income": profit,
                "early_withdrawal_penalty": 0,
                "health_premiums": 0,
                "pension_contributions": 0,
                "extra_interest": 1_000,
            }
            for profit in (433, 434)
        ]
    )
    @hypothesis.given(st.lists(case(), min_size=1, max_size=8))
    def test_properties(cases):
        assert_properties(cases)
