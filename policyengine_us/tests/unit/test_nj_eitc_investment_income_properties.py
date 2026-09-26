"""Properties of the New Jersey EITC investment income test.

N.J.S.A. 54A:4-7a.(4) lets a childless filer who is ineligible for the
federal EITC because of age claim the New Jersey EITC, but the filer "shall
meet all qualifications, except for the minimum or maximum age, for the
federal earned income tax credit". One of those qualifications is the
26 U.S.C. § 32(i) limit on investment income. IRS Publication 596 Worksheet 1
computes that income with the passive basket floored at zero (line 13) before
it is added to interest (line 14), so a rental or passive loss cannot offset
interest.

Each test evaluates a grid of New Jersey tax units in one vectorized
simulation and checks, for every grid point:

- `nj_eitc_income_eligible` matches a closed-form Worksheet 1 reference,
  interest + max(0, rental + passive) <= the Rule 6 limit, for tax units
  under the no-child income limit, and is false for those at or above it;
- it agrees with the federal `eitc_investment_income_eligible` wherever the
  tax unit is under that income limit;
- adding non-positive rental or passive amounts never changes the result of
  the investment income test, and never gives a filer who fails it on
  interest alone a federal or New Jersey EITC.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

# IRS Publication 596 for each year: the Rule 6 investment income limit
# (Worksheet 1, line 15), and the earned income and AGI limit for filers
# without a qualifying child, as (single, married filing jointly).
PUB_596 = {
    2021: (10_000, (21_430, 27_380)),
    2022: (10_300, (16_480, 22_610)),
    2023: (11_000, (17_640, 24_210)),
    2024: (11_600, (18_591, 25_511)),
    2025: (11_950, (19_104, 26_214)),
}
WAGES = 3_000
RENTALS = [-10_000, -3_000, 0, 2_000, 5_000]
PASSIVES = [-10_000, -3_000, 0, 1_000]


def interest_amounts(limit):
    return [0, 2_500, 8_000, limit, limit + 1, 12_500, 20_000]


def grid(year):
    limit, _ = PUB_596[year]
    points = list(itertools.product(interest_amounts(limit), RENTALS, PASSIVES))
    interest, rental, passive = (
        np.array(column, dtype=float) for column in zip(*points)
    )
    return interest, rental, passive


def grid_simulation(year, joint):
    """One childless tax unit per grid point, all in New Jersey.

    Joint tax units put the interest on the head and the rental and passive
    amounts on the spouse, so the test also covers aggregation across the
    tax unit.
    """
    interest, rental, passive = grid(year)
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i in range(len(interest)):
        head = {
            "age": {year: 20},
            "employment_income": {year: WAGES},
            "taxable_interest_income": {year: interest[i].item()},
        }
        other = {
            "rental_income": {year: rental[i].item()},
            "partnership_s_corp_income": {year: passive[i].item()},
            "passive_partnership_s_corp_income": {year: passive[i].item()},
        }
        members = [f"head{i}"]
        if joint:
            situation["people"][f"spouse{i}"] = {"age": {year: 20}, **other}
            members.append(f"spouse{i}")
        else:
            head.update(other)
        situation["people"][f"head{i}"] = head
        situation["tax_units"][f"t{i}"] = {"members": members}
        situation["households"][f"h{i}"] = {
            "members": members,
            "state_code": {year: "NJ"},
        }
    return Simulation(situation=situation)


YEARS = list(PUB_596)
CASES = [(year, joint) for year in YEARS for joint in (False, True)]


@pytest.fixture(
    scope="module",
    params=CASES,
    ids=lambda c: f"{c[0]}-{'joint' if c[1] else 'single'}",
)
def case(request):
    year, joint = request.param
    sim = grid_simulation(year, joint)
    interest, rental, passive = grid(year)
    investment_limit, income_limits = PUB_596[year]
    return {
        "year": year,
        "sim": sim,
        "interest": interest,
        "rental": rental,
        "passive": passive,
        "investment_limit": investment_limit,
        "income_limit": income_limits[joint],
        "agi": sim.calculate("adjusted_gross_income", year),
        "nj_eligible": sim.calculate("nj_eitc_income_eligible", year),
    }


def worksheet_1_investment_income(interest, rental, passive):
    # Lines 11-13 net the passive basket and floor it at zero; line 14 adds
    # it to interest.
    return interest + np.maximum(0, rental + passive)


def test_agi_is_the_sum_of_the_inputs(case):
    """Precondition: the grid's AGI is wages plus the three amounts."""
    expected = WAGES + case["interest"] + case["rental"] + case["passive"]
    np.testing.assert_allclose(case["agi"], expected)


def test_matches_worksheet_1_reference(case):
    investment_income = worksheet_1_investment_income(
        case["interest"], case["rental"], case["passive"]
    )
    under_income_limit = case["agi"] < case["income_limit"]
    expected = under_income_limit & (investment_income <= case["investment_limit"])
    np.testing.assert_array_equal(case["nj_eligible"], expected)
    # Guard against a vacuous pass: the grid has tax units under the income
    # limit on both sides of the investment income limit, and tax units whose
    # interest alone exceeds the limit but whose losses would bring a netted
    # sum under it.
    assert expected.any() and (under_income_limit & ~expected).any()
    netted = case["interest"] + case["rental"] + case["passive"]
    assert (
        under_income_limit
        & (investment_income > case["investment_limit"])
        & (netted <= case["investment_limit"])
    ).any()


def test_agrees_with_federal_investment_income_test(case):
    federal = case["sim"].calculate("eitc_investment_income_eligible", case["year"])
    under_income_limit = case["agi"] < case["income_limit"]
    np.testing.assert_array_equal(
        case["nj_eligible"][under_income_limit], federal[under_income_limit]
    )


def test_losses_do_not_change_the_investment_income_test(case):
    year, sim = case["year"], case["sim"]
    interest, rental, passive = case["interest"], case["rental"], case["passive"]
    federal = sim.calculate("eitc_investment_income_eligible", year)
    eitc = sim.calculate("eitc", year)
    nj_eitc = sim.calculate("nj_eitc", year)
    # For each interest amount, the tax unit with no rental or passive amount.
    interest_only = {
        amount: np.flatnonzero((interest == amount) & (rental == 0) & (passive == 0))[0]
        for amount in np.unique(interest)
    }
    base = np.array([interest_only[amount] for amount in interest])
    losses = (rental <= 0) & (passive <= 0)
    np.testing.assert_array_equal(federal[losses], federal[base][losses])
    fails_on_interest = losses & (interest > case["investment_limit"])
    assert fails_on_interest.any()
    assert not case["nj_eligible"][fails_on_interest].any()
    np.testing.assert_array_equal(eitc[fails_on_interest], 0)
    np.testing.assert_array_equal(nj_eitc[fails_on_interest], 0)
