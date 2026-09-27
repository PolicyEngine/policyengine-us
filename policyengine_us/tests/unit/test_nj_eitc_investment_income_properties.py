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
# (age, wages) profiles. Age 20 fails the federal no-child age test except
# in 2021, so it reaches New Jersey's age-expanded path; age 30 passes it, so
# with $3,000 of wages the federal credit turns only on investment income.
# The higher wages put tax units that pass the investment income test above
# the single, and then the joint, income limit.
PROFILES = [(20, 3_000), (30, 3_000), (30, 15_000), (20, 24_000)]
RENTALS = [-10_000, -3_000, 0, 2_000, 5_000]
PASSIVES = [-10_000, -3_000, 0, 1_000]


def interest_amounts(limit):
    return [0, 2_500, 8_000, limit, limit + 1, 12_500, 20_000]


def grid(year):
    limit, _ = PUB_596[year]
    points = [
        (profile, age, wages, interest, rental, passive)
        for profile, (age, wages) in enumerate(PROFILES)
        for interest, rental, passive in itertools.product(
            interest_amounts(limit), RENTALS, PASSIVES
        )
    ]
    columns = ("profile", "age", "wages", "interest", "rental", "passive")
    return {
        name: np.array(column, dtype=float)
        for name, column in zip(columns, zip(*points))
    }


def grid_simulation(year, joint):
    """One childless tax unit per grid point, all in New Jersey.

    Joint tax units put the wages and interest on the head and the rental
    and passive amounts on the spouse, so the test also covers aggregation
    across the tax unit.
    """
    g = grid(year)
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i in range(len(g["interest"])):
        age = g["age"][i].item()
        head = {
            "age": {year: age},
            "employment_income": {year: g["wages"][i].item()},
            "taxable_interest_income": {year: g["interest"][i].item()},
        }
        other = {
            "rental_income": {year: g["rental"][i].item()},
            "partnership_s_corp_income": {year: g["passive"][i].item()},
            "passive_partnership_s_corp_income": {year: g["passive"][i].item()},
        }
        members = [f"head{i}"]
        if joint:
            situation["people"][f"spouse{i}"] = {"age": {year: age}, **other}
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
    investment_limit, income_limits = PUB_596[year]
    return {
        "year": year,
        "joint": joint,
        "sim": sim,
        **grid(year),
        "investment_limit": investment_limit,
        "income_limit": income_limits[joint],
        "income_limits": income_limits,
        "agi": sim.calculate("adjusted_gross_income", year),
        "nj_eligible": sim.calculate("nj_eitc_income_eligible", year),
    }


def worksheet_1_investment_income(case):
    # Lines 11-13 net the passive basket and floor it at zero; line 14 adds
    # it to interest.
    return case["interest"] + np.maximum(0, case["rental"] + case["passive"])


def test_grid_preconditions(case):
    """AGI is wages plus the three amounts, filing status follows the tax
    unit's size, and no AGI falls between the completed phase-out the model
    computes and the rounded Publication 596 income limit (for example,
    21,426.99 against $21,430 in 2021), so the reference comparison tests
    the investment income rule rather than that rounding."""
    year, joint = case["year"], case["joint"]
    expected = case["wages"] + case["interest"] + case["rental"] + case["passive"]
    np.testing.assert_allclose(case["agi"], expected)
    is_joint = case["sim"].calculate("tax_unit_is_joint", year)
    assert np.all(is_joint == joint)
    p = case["sim"].tax_benefit_system.parameters(year).gov.irs.credits.eitc
    completed_phase_out = (
        p.max.calc(0) / p.phase_out.rate.calc(0)
        + p.phase_out.start.calc(0)
        + joint * p.phase_out.joint_bonus.calc(0)
    )
    low, high = sorted([completed_phase_out, case["income_limit"]])
    assert not ((case["agi"] >= low) & (case["agi"] < high)).any()


def test_matches_worksheet_1_reference(case):
    investment_income = worksheet_1_investment_income(case)
    passes_investment = investment_income <= case["investment_limit"]
    under_income_limit = case["agi"] < case["income_limit"]
    expected = under_income_limit & passes_investment
    np.testing.assert_array_equal(case["nj_eligible"], expected)
    # Guard against a vacuous pass. The grid has tax units under the income
    # limit on both sides of the investment income limit; tax units whose
    # interest alone exceeds the limit but whose losses would bring a netted
    # sum under it; tax units that pass the investment income test but not
    # the income limit; and tax units that pass it with AGI between the
    # single and joint limits, where the two filing statuses must differ.
    assert expected.any() and (under_income_limit & ~passes_investment).any()
    netted = case["interest"] + case["rental"] + case["passive"]
    assert (
        under_income_limit & ~passes_investment & (netted <= case["investment_limit"])
    ).any()
    assert (passes_investment & ~under_income_limit).any()
    single_limit, joint_limit = case["income_limits"]
    between = (case["agi"] >= single_limit) & (case["agi"] < joint_limit)
    assert (passes_investment & between).any()


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
    # For each profile and interest amount, the tax unit with no rental or
    # passive amount.
    no_rental_or_passive = (rental == 0) & (passive == 0)
    interest_only = {
        (profile, amount): i
        for i, (profile, amount) in enumerate(zip(case["profile"], interest))
        if no_rental_or_passive[i]
    }
    base = np.array([interest_only[key] for key in zip(case["profile"], interest)])
    losses = (rental <= 0) & (passive <= 0)
    np.testing.assert_array_equal(federal[losses], federal[base][losses])
    fails_on_interest = losses & (interest > case["investment_limit"])
    assert not case["nj_eligible"][fails_on_interest].any()
    np.testing.assert_array_equal(eitc[fails_on_interest], 0)
    np.testing.assert_array_equal(nj_eitc[fails_on_interest], 0)
    # Guard against a vacuous pass: filers with the same profiles and losses
    # who pass the investment income test do get a federal and a New Jersey
    # credit, so the zeros above come from the investment income test.
    assert fails_on_interest.any()
    passes_on_interest = losses & (interest <= case["investment_limit"])
    assert (eitc[passes_on_interest] > 0).any()
    assert (nj_eitc[passes_on_interest & (case["age"] == 20)] > 0).any()
