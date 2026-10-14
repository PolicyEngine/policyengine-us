"""Invariant tests: disability benefits and unemployment compensation in the
Montana elderly homeowner/renter credit.

MCA 15-30-2337(9)(a) counts federal adjusted gross income "plus all
nontaxable income", and (4) counts "all income received by all individuals
of a household". 2024 Schedule 2EC line 14 counts "the total of unemployment
compensation received during the year"; the 2014-2023 instructions list
disability benefits. The model leaves employment disability benefits out of
federal AGI, and in 2020 IRC 85(c) excluded up to 10_200 of unemployment
compensation from it. Federal AGI counts the taxable part of a filer's
compensation and a dependent's own gross income all of a dependent's.

For a claimant aged 66 (taxable pension, unemployment compensation,
disability benefits, property tax) living with one other adult (unemployment
compensation, disability benefits), in 2019, 2020, 2021 and 2024, in three
arrangements:

  dependent: one return, the other adult a 20-year-old student dependent;
  own_return: two returns, the other adult (45) filing their own;
  joint: one joint return, the other adult (60) the claimant's spouse;

over a grid of amounts that puts the compensation under and over the 10_200
limit, and income under and over the 150_000 cutoff:

1. The household's gross household income is the pension plus every
   member's unemployment compensation and disability benefits, each once,
   plus the refundable credits the household received (read from the model;
   no one has earnings, so these are the recovery rebate credits).
2. The credit equals an independent reading of the schedule (standard
   exclusion, Household Income Reduction Table, cap, Credit Multiplier
   Table), lies between zero and the cap, and is zero at 45_000 or more.
3. More unemployment compensation or disability benefits never raise the
   credit while the refundable credits stay the same.

The YAML cases pin worked examples from each year's form. This test adds
what they cannot: every arrangement and year at once against a reference
written from the statute rather than the model's income paths, so a double
count through federal AGI, dependent_gross_income or the 2020 exclusion
shows up. It builds one vectorized Simulation.
"""

import gc
import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

YEARS = [2019, 2020, 2021, 2024]
ARRANGEMENTS = ["dependent", "own_return", "joint"]
PENSIONS = [12_000, 160_000]
CLAIMANT_UC = [0, 6_000, 15_000]
MEMBER_UC = [0, 4_000, 12_000]
CLAIMANT_DISABILITY = [0, 3_000]
MEMBER_DISABILITY = [0, 5_000]
PROPERTY_TAX = 1_500
INCOME_LIMIT = 45_000
TOLERANCE = 0.01
# Standard exclusion and cap: $6,300 and $1,000 through 2021; HB 191 (2021)
# raised them to $12,600 and $1,150 from 2022.
EXCLUSION = {2019: 6_300, 2020: 6_300, 2021: 6_300, 2024: 12_600}
CAP = {2019: 1_000, 2020: 1_000, 2021: 1_000, 2024: 1_150}
# Household Income Reduction Table: lower bounds and rates.
REDUCTION_TABLE = [
    (0, 0),
    (2_000, 0.006),
    (3_000, 0.016),
    (4_000, 0.024),
    (5_000, 0.028),
    (6_000, 0.032),
    (7_000, 0.035),
    (8_000, 0.039),
    (9_000, 0.042),
    (10_000, 0.045),
    (11_000, 0.048),
    (12_000, 0.05),
]
# Credit Multiplier Table: lower bounds of gross household income.
MULTIPLIER_TABLE = [
    (0, 1),
    (35_000, 0.4),
    (37_501, 0.3),
    (40_001, 0.2),
    (42_501, 0.1),
    (45_000, 0),
]
CASES = [
    dict(
        arrangement=arrangement,
        pension=pension,
        claimant_uc=claimant_uc,
        member_uc=member_uc,
        claimant_disability=claimant_disability,
        member_disability=member_disability,
    )
    for (
        arrangement,
        pension,
        claimant_uc,
        member_uc,
        claimant_disability,
        member_disability,
    ) in itertools.product(
        ARRANGEMENTS,
        PENSIONS,
        CLAIMANT_UC,
        MEMBER_UC,
        CLAIMANT_DISABILITY,
        MEMBER_DISABILITY,
    )
]


def build_situation():
    def every_year(value):
        return {year: value for year in YEARS}

    people, tax_units, marital_units, households = {}, {}, {}, {}
    for i, c in enumerate(CASES):
        claimant, member = f"claimant_{i}", f"member_{i}"
        arrangement = c["arrangement"]
        people[claimant] = {
            "age": every_year(66),
            "taxable_pension_income": every_year(c["pension"]),
            "unemployment_compensation": every_year(c["claimant_uc"]),
            "disability_benefits": every_year(c["claimant_disability"]),
            "real_estate_taxes": every_year(PROPERTY_TAX),
            "ssi": every_year(0),
            "is_tax_unit_dependent": every_year(False),
        }
        people[member] = {
            "age": every_year(
                {"dependent": 20, "own_return": 45, "joint": 60}[arrangement]
            ),
            "is_full_time_student": every_year(arrangement == "dependent"),
            "unemployment_compensation": every_year(c["member_uc"]),
            "disability_benefits": every_year(c["member_disability"]),
            "ssi": every_year(0),
            "is_tax_unit_dependent": every_year(arrangement == "dependent"),
        }
        if arrangement == "own_return":
            tax_units[f"tax_unit_{i}"] = {"members": [claimant]}
            tax_units[f"tax_unit_{i}_member"] = {"members": [member]}
        else:
            tax_units[f"tax_unit_{i}"] = {"members": [claimant, member]}
        if arrangement == "joint":
            marital_units[f"marital_unit_{i}"] = {"members": [claimant, member]}
        else:
            marital_units[f"marital_unit_{i}"] = {"members": [claimant]}
            marital_units[f"marital_unit_{i}_member"] = {"members": [member]}
        households[f"household_{i}"] = {
            "members": [claimant, member],
            "state_code": every_year("MT"),
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "households": households,
    }


@pytest.fixture(scope="module")
def results():
    """Household totals by year: gross household income, the credit, and
    the refundable credits received."""
    simulation = Simulation(situation=build_situation())

    def by_household(variable, year):
        return np.asarray(simulation.calculate(variable, year, map_to="household"))

    results = {
        year: {
            "gross_household_income": by_household(
                "mt_elderly_homeowner_or_renter_credit_gross_household_income",
                year,
            ),
            "credit": by_household("mt_elderly_homeowner_or_renter_credit", year),
            "refundable_credits": by_household(
                "mt_elderly_homeowner_or_renter_credit_federal_refundable_credits",
                year,
            )
            + by_household("mt_refundable_credits_before_renter_credit", year),
        }
        for year in YEARS
    }
    # Keep only the arrays: free the simulation before the rest of the
    # process's tests run.
    del simulation
    gc.collect()
    return results


def lookup(table, amount):
    rate = 0
    for lower, value in table:
        if amount >= lower:
            rate = value
    return rate


def expected_credit(year, gross_household_income):
    household_income = max(gross_household_income - EXCLUSION[year], 0)
    net_household_income = household_income * lookup(REDUCTION_TABLE, household_income)
    uncapped = max(PROPERTY_TAX - net_household_income, 0)
    return min(uncapped, CAP[year]) * lookup(MULTIPLIER_TABLE, gross_household_income)


def tolerance(amount):
    return max(TOLERANCE, 8 * float(np.spacing(np.float32(abs(amount)))))


@pytest.mark.parametrize("year", YEARS)
def test_each_amount_counts_once(results, year):
    r = results[year]
    for i, c in enumerate(CASES):
        expected = (
            c["pension"]
            + c["claimant_uc"]
            + c["member_uc"]
            + c["claimant_disability"]
            + c["member_disability"]
            + r["refundable_credits"][i]
        )
        assert r["gross_household_income"][i] == pytest.approx(
            expected, abs=tolerance(expected)
        ), (year, c)


@pytest.mark.parametrize("year", YEARS)
def test_credit_follows_the_schedule(results, year):
    r = results[year]
    for i, c in enumerate(CASES):
        ghi = float(r["gross_household_income"][i])
        credit = float(r["credit"][i])
        tol = tolerance(ghi)
        assert credit == pytest.approx(expected_credit(year, ghi), abs=tol), (
            year,
            c,
        )
        assert -tol <= credit <= CAP[year] + tol, (year, c)
        if ghi >= INCOME_LIMIT:
            assert credit == 0, (year, c)


@pytest.mark.parametrize("year", YEARS)
def test_more_income_never_raises_the_credit(results, year):
    r = results[year]
    index = {tuple(sorted(c.items())): i for i, c in enumerate(CASES)}
    axes = {
        "claimant_uc": CLAIMANT_UC,
        "member_uc": MEMBER_UC,
        "claimant_disability": CLAIMANT_DISABILITY,
        "member_disability": MEMBER_DISABILITY,
    }
    compared = 0
    for i, c in enumerate(CASES):
        for key, values in axes.items():
            position = values.index(c[key])
            if position + 1 == len(values):
                continue
            j = index[tuple(sorted({**c, key: values[position + 1]}.items()))]
            if r["refundable_credits"][j] != r["refundable_credits"][i]:
                continue
            compared += 1
            tol = tolerance(r["gross_household_income"][j])
            assert r["credit"][j] <= r["credit"][i] + tol, (year, c, key)
    assert compared > 0


def test_worked_example(results):
    """2020 Elderly Homeowner/Renter Credit Schedule, own_return arrangement:
    the claimant's pension 12_000 and unemployment compensation 6_000, all
    excluded from federal AGI; the other adult's 12_000 of compensation,
    1_800 of it in federal AGI; each return's recovery rebate credit 1_800.
    Line 1 = 12_000 + 1_800; line 7 = 3_600; line 8 = 6_000 + 10_200; line
    10 = 33_600; line 12 = 27_300; line 14 = 1_365; line 19 = 135; line 22 =
    135 at the 100% multiplier."""
    i = CASES.index(
        dict(
            arrangement="own_return",
            pension=12_000,
            claimant_uc=6_000,
            member_uc=12_000,
            claimant_disability=0,
            member_disability=0,
        )
    )
    r = results[2020]
    assert r["refundable_credits"][i] == pytest.approx(3_600, abs=TOLERANCE)
    assert r["gross_household_income"][i] == pytest.approx(33_600, abs=TOLERANCE)
    assert r["credit"][i] == pytest.approx(135, abs=TOLERANCE)
