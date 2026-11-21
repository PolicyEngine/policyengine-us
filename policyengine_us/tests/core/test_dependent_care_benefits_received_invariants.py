"""Form 2441 line 15 properties for grace-period carryovers and forfeitures.

Form 2441 line 15 adds line 13 (prior-year benefits used in this year's grace
period) to line 12 and subtracts line 14 (amounts forfeited or carried
forward). Line 12 is dependent_care_employer_benefits: W-2 box 10, not
counting any amount above the plan's exclusion, which box 1 already includes
as wages. Line 25 excludes the smallest of line 15, line 16 qualified
expenses, earned income and the line 21 cap, and line 26 taxes the rest of
line 15. FTB 3506 lines 14 to 16 repeat lines 13 to 15 for California, with
California's own cap, and count line 13 in every year. For 2021 and 2022,
when line 21 adds line 13 to the cap under temporary relief rules, the federal
calculation leaves line 13 out of both line 15 and the cap, so those years'
federal results must match a return without the carryover.

Each seeded filer has line 12 benefits (above $5,000 only when they come from
more than one employer's plan), an optional forfeiture of part of them and an
optional carryover. Wages other than line 12 benefits are fixed, and the
benefits sit inside employment_income as a pre-tax deduction. Qualified
expenses are an explicit tax-unit fact, as Form 2441 line 16 is.

https://www.irs.gov/pub/irs-prior/f2441--2025.pdf#page=2
https://www.irs.gov/pub/irs-prior/i2441--2025.pdf#page=5
https://www.irs.gov/pub/irs-prior/f2441--2022.pdf#page=2
https://www.ftb.ca.gov/forms/2025/2025-3506.pdf#page=2
https://www.ftb.ca.gov/forms/2021/2021-3506-instructions.html
"""

import numpy as np
import pytest

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars
SEED = 20261121
# Form 2441 line 21 cap (joint or unmarried, ordinary separate), by year.
FEDERAL_CAP = {
    2020: (5_000, 2_500),
    2021: (10_500, 5_250),
    2022: (5_000, 2_500),
    2023: (5_000, 2_500),
    2025: (5_000, 2_500),
    2026: (7_500, 3_750),
}
# FTB 3506 Part IV line 22.
CALIFORNIA_CAP = (5_000, 2_500)
RELIEF_YEARS = {2021, 2022}
FILING_STATUSES = ["SINGLE", "JOINT", "HEAD_OF_HOUSEHOLD", "SEPARATE"]


def _units(n=120):
    rng = np.random.default_rng(SEED)

    def filer():
        line_12 = float(
            [0, rng.integers(1, 5_001), rng.integers(5_000, 9_001)][rng.integers(0, 3)]
        )
        forfeited = float(rng.integers(0, line_12 + 1)) if rng.random() < 0.5 else 0.0
        return {
            "wages": float(rng.integers(0, 120_001)),
            "line_12": line_12,
            "carryover": float(rng.integers(1, 3_001)) if rng.random() < 0.5 else 0.0,
            "forfeited": forfeited,
        }

    units = []
    for _ in range(n):
        filing_status = str(rng.choice(FILING_STATUSES))
        units.append(
            {
                "filing_status": filing_status,
                "filers": [filer()] + ([filer()] if filing_status == "JOINT" else []),
                "children": int(rng.integers(1, 3)),
                "expenses": float(rng.integers(0, 12_001)),
            }
        )
    return units


def _situation(units, year, with_carryover=True):
    people, tax_units, households, marital_units = {}, {}, {}, {}
    for i, unit in enumerate(units):
        members = []
        for k, f in enumerate(unit["filers"]):
            name = f"filer_{i}_{k}"
            people[name] = {
                "age": {year: 40},
                "is_tax_unit_head": {year: k == 0},
                "is_tax_unit_spouse": {year: k == 1},
                "employment_income": {year: f["wages"] + f["line_12"]},
                "dependent_care_employer_benefits": {year: f["line_12"]},
                "dependent_care_employer_benefits_forfeited_or_carried_forward": {
                    year: f["forfeited"]
                },
                "dependent_care_employer_benefits_prior_year_carryover": {
                    year: f["carryover"] if with_carryover else 0.0
                },
            }
            members.append(name)
        marital_units[f"couple_{i}"] = {"members": list(members)}
        for j in range(unit["children"]):
            child = f"child_{i}_{j}"
            people[child] = {"age": {year: 5}, "is_tax_unit_dependent": {year: True}}
            members.append(child)
            marital_units[f"single_{i}_{j}"] = {"members": [child]}
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            "filing_status": {year: unit["filing_status"]},
            "dependent_care_assistance_qualified_expenses": {year: unit["expenses"]},
            # An isolated component input, as in the exclusion invariants test.
            "ca_cdcc_min_head_spouse_earned": {
                year: min(f["wages"] for f in unit["filers"])
            },
        }
        households[f"household_{i}"] = {
            "members": members,
            "state_code": {year: "CA"},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "households": households,
        "marital_units": marital_units,
    }


def _line_15(filer, count_line_13):
    carryover = filer["carryover"] if count_line_13 else 0.0
    return max(filer["line_12"] + carryover - filer["forfeited"], 0.0)


def _expected_exclusion(unit, caps, count_line_13):
    line_15 = sum(_line_15(f, count_line_13) for f in unit["filers"])
    cap = caps[1] if unit["filing_status"] == "SEPARATE" else caps[0]
    earned = min(f["wages"] for f in unit["filers"])
    return min(line_15, unit["expenses"], cap, earned)


@pytest.mark.parametrize("year", sorted(FEDERAL_CAP))
def test_line_15_carryovers_and_forfeitures(year):
    units = _units()
    sim = Simulation(situation=_situation(units, year))
    exclusion = sim.calculate("dependent_care_assistance_exclusion", year)
    california = sim.calculate("ca_dependent_care_assistance_exclusion", year)
    taxable = sim.calculate("taxable_dependent_care_benefits", year)
    income_tax_wages = sim.calculate("irs_employment_income", year)
    payroll_tax_wages = sim.calculate("payroll_tax_gross_wages", year)
    count_line_13 = year not in RELIEF_YEARS

    i = 0
    for u, unit in enumerate(units):
        # 1. Line 25 and FTB 3506 line 26 from line 15 (FTB line 16), with
        # California counting line 13 in every year.
        expected = _expected_exclusion(unit, FEDERAL_CAP[year], count_line_13)
        assert exclusion[u] == pytest.approx(expected, abs=TOLERANCE)
        assert california[u] == pytest.approx(
            _expected_exclusion(unit, CALIFORNIA_CAP, True), abs=TOLERANCE
        )
        line_15 = [_line_15(f, count_line_13) for f in unit["filers"]]
        unit_taxable = max(sum(line_15) - expected, 0.0)
        for k, f in enumerate(unit["filers"]):
            # 2. Line 26, split by each filer's own line 15 amount.
            share = line_15[k] / sum(line_15) if sum(line_15) > 0 else 0.0
            assert taxable[i] == pytest.approx(unit_taxable * share, abs=TOLERANCE)
            # 3. Lines 13 and 14 leave income tax and FICA wages unchanged.
            assert income_tax_wages[i] == pytest.approx(f["wages"], abs=TOLERANCE)
            assert payroll_tax_wages[i] == pytest.approx(f["wages"], abs=TOLERANCE)
            i += 1
        # Children have no line 15 and no taxable benefits.
        for _ in range(unit["children"]):
            assert taxable[i] == 0
            i += 1


@pytest.mark.parametrize("year", sorted(RELIEF_YEARS))
def test_relief_years_ignore_line_13(year):
    # 4. In 2021 and 2022 the carryover changes no federal result, as on
    # main. California counts it (checked above).
    units = _units()
    with_carryover = Simulation(situation=_situation(units, year))
    without = Simulation(situation=_situation(units, year, with_carryover=False))
    for variable in [
        "dependent_care_assistance_exclusion",
        "taxable_dependent_care_benefits",
        "cdcc_limit",
    ]:
        np.testing.assert_array_equal(
            with_carryover.calculate(variable, year),
            without.calculate(variable, year),
        )
