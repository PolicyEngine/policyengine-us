"""Invariants for Maine's childless EITC age expansion, 36 M.R.S. 5219-S(5)-(6).

Subsection 6 adds to Maine's eligible individuals a filer without a
qualifying child "who is at least 18 years of age and has not attained 25
years of age before the close of the taxable year" and who meets 26 U.S.C.
32(c)(1)(A)(ii)(I) and (III). Subsection 5 computes that filer's credit "in
the same manner as it would be calculated if that individual were eligible
for a federal earned income credit". The federal age test is 25 to 64; for
2021, 32(n)(1)-(2) lowered the minimum to 19, or 24 for a specified student,
and removed the maximum.

Each batch of households runs three times:

- as is;
- under a reform that removes the federal age test, so that every household
  meets it and nothing else changes ("otherwise identical" and federally
  eligible);
- with every student flag cleared.

The checks:

1. Twin equality. A household with a filer or spouse aged 18 to 24, or one
   that meets the federal age test, gets the same Maine credit as its twin
   without the federal age test. A filer who fails only the age test
   therefore gets what an otherwise identical federally eligible filer gets;
   a filer who also fails another federal requirement gets nothing either
   way.
2. Student status never changes the Maine credit: in 2021 it moves a filer
   aged 19 to 23 between the federal path and the Maine pro forma, at the
   same amount.
3. The cohort matches an oracle written from the statute's ages: no
   qualifying child, a filer or spouse aged 18 to 24, and neither meets the
   federal age test. It also matches the federal code: for a childless
   household with no filer claimable elsewhere, the cohort is "a filer or
   spouse aged 18 to 24" and "not eitc_demographic_eligible".
4. One path only. Inside the cohort the federal credit is zero, outside it
   the pro forma is zero, and the Maine credit is the statutory rate times
   their sum.
5. A childless household with no filer or spouse aged 18 to 24 that fails
   the federal age test gets no Maine credit.

The pro forma applies no take-up and no separate-return or section 911 rule,
as on main (separate returns follow #10307; section 911 is #10525), so every
household here takes up the EITC, files single or joint, and has no foreign
earned income. The Hypothesis version is in
test_me_childless_eitc_age_gate_property.py.
"""

from functools import cache

import numpy as np
from policyengine_core.reforms import Reform

from policyengine_us import CountryTaxBenefitSystem, Simulation

AGE = "gov.irs.credits.eitc.eligibility.age"

TAX_UNIT_OUTPUTS = [
    "eitc",
    "eitc_eligible",
    "eitc_demographic_eligible",
    "eitc_child_count",
    "head_or_spouse_is_dependent_elsewhere_without_filing_exception",
    "me_childless_eitc_age_eligible",
    "me_pro_forma_childless_eitc",
    "me_eitc",
]


@cache
def no_federal_age_test_system():
    # One reformed system serves every household batch.
    always = "2010-01-01.2100-12-31"
    reform = Reform.from_dict(
        {
            f"{AGE}.min": {always: 0},
            f"{AGE}.min_student": {always: 0},
            f"{AGE}.max": {always: 200},
        },
        country_id="us",
    )
    return CountryTaxBenefitSystem(reform=reform)


def federal_age_limits(year):
    """Minimum, student minimum and maximum childless ages under 26 U.S.C. 32."""
    if year == 2021:
        # 32(n)(1)-(2), added by ARPA section 9621.
        return 19, 24, np.inf
    # 32(c)(1)(A)(ii)(II): attained 25 but not 65.
    return 25, 25, 64


def maine_rate(year, childless):
    """36 M.R.S. 5219-S(1) and (1-A), resident rates."""
    if year == 2020:
        return 0.25 if childless else 0.12
    if year == 2021:
        return 0.20
    return 0.50 if childless else 0.25


def filers(h):
    """(age, student) for the head and, on a joint return, the spouse."""
    out = [(h["head_age"], h["head_student"])]
    if h["spouse"] is not None:
        out.append((h["spouse"]["age"], h["spouse"]["student"]))
    return out


def meets_federal_age(h, year):
    minimum, student_minimum, maximum = federal_age_limits(year)
    return any(
        (student_minimum if student else minimum) <= age <= maximum
        for age, student in filers(h)
    )


def in_maine_range(h):
    return any(18 <= age <= 24 for age, _ in filers(h))


def build_situation(households, year, students=True):
    people, tax_units, marital_units = {}, {}, {}
    groups = {"households": {}, "spm_units": {}, "families": {}}
    for i, h in enumerate(households):
        head = f"head_{i}"
        people[head] = {
            "age": {year: h["head_age"]},
            "is_full_time_student": {year: students and h["head_student"]},
            "employment_income": {year: h["wages"]},
            "unemployment_compensation": {year: h["unemployment"]},
            "taxable_interest_income": {year: h["interest"]},
            "ssn_card_type": {year: "CITIZEN" if h["ssn"] else "OTHER_NON_CITIZEN"},
            "claimed_as_dependent_on_another_return": {year: h["claimed"]},
        }
        members = [head]
        marital_units[f"marital_unit_{i}"] = {"members": [head]}
        tax_unit = {"takes_up_eitc": {year: True}}
        spouse_h = h["spouse"]
        if spouse_h is not None:
            spouse = f"spouse_{i}"
            people[spouse] = {
                "age": {year: spouse_h["age"]},
                "is_full_time_student": {year: students and spouse_h["student"]},
                "employment_income": {year: spouse_h["wages"]},
                "ssn_card_type": {
                    year: "CITIZEN" if spouse_h["ssn"] else "OTHER_NON_CITIZEN"
                },
            }
            members.append(spouse)
            marital_units[f"marital_unit_{i}"]["members"].append(spouse)
            tax_unit["filing_status"] = {year: "JOINT"}
        for j, age in enumerate(h["child_ages"]):
            child = f"child_{i}_{j}"
            people[child] = {"age": {year: age}}
            members.append(child)
            marital_units[f"marital_unit_{i}_{j}"] = {"members": [child]}
        tax_unit["members"] = members
        tax_units[f"tax_unit_{i}"] = tax_unit
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "ME"},
        }
        groups["spm_units"][f"spm_unit_{i}"] = {"members": members}
        groups["families"][f"family_{i}"] = {"members": members}
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        **groups,
    }


def calculate(households, year, students=True, federal_age_test=True):
    system = (
        {} if federal_age_test else {"tax_benefit_system": no_federal_age_test_system()}
    )
    simulation = Simulation(
        situation=build_situation(households, year, students), **system
    )
    return {v: np.asarray(simulation.calculate(v, year)) for v in TAX_UNIT_OUTPUTS}


def assert_invariants(households, year, r, twin, non_student):
    # Model outputs are float32, so comparisons allow a cent.
    tol = 0.01
    childless = r["eitc_child_count"] == 0
    in_range = np.array([in_maine_range(h) for h in households])
    federal_age = np.array([meets_federal_age(h, year) for h in households])
    cohort = r["me_childless_eitc_age_eligible"]

    # 1. Twin equality, wherever Maine's age rules or the federal ones admit
    # the household (and wherever it has a qualifying child, for which age
    # does not matter).
    admitted = in_range | federal_age | ~childless
    np.testing.assert_allclose(
        r["me_eitc"][admitted], twin["me_eitc"][admitted], atol=tol
    )
    # The twin never uses the pro forma: every household meets its age test.
    assert not twin["me_childless_eitc_age_eligible"].any()

    # 2. Student status never changes the Maine credit.
    np.testing.assert_allclose(r["me_eitc"], non_student["me_eitc"], atol=tol)

    # 3. The cohort, from the statute's ages and from the federal code.
    np.testing.assert_array_equal(cohort, childless & in_range & ~federal_age)
    claimable = r["head_or_spouse_is_dependent_elsewhere_without_filing_exception"]
    plain = childless & ~claimable
    np.testing.assert_array_equal(
        cohort[plain], (in_range & ~r["eitc_demographic_eligible"])[plain]
    )

    # 4. One path only, at the statutory rate.
    assert not (cohort & r["eitc_eligible"]).any()
    assert (r["eitc"][cohort] == 0).all()
    assert (r["me_pro_forma_childless_eitc"][~cohort] == 0).all()
    rate = np.array([maine_rate(year, c) for c in childless])
    np.testing.assert_allclose(
        r["me_eitc"],
        rate * (r["eitc"] + r["me_pro_forma_childless_eitc"]),
        atol=tol,
    )

    # 5. Outside both age rules a childless household gets nothing.
    neither = childless & ~in_range & ~federal_age
    assert (r["me_eitc"][neither] == 0).all()


def check(households, year):
    r = calculate(households, year)
    twin = calculate(households, year, federal_age_test=False)
    non_student = calculate(households, year, students=False)
    assert_invariants(households, year, r, twin, non_student)
    return r, twin


def spouse(age, student=False, wages=0, ssn=True):
    return {"age": age, "student": student, "wages": wages, "ssn": ssn}


GRID = [
    {
        "head_age": head_age,
        "head_student": head_student,
        "spouse": spouse_h,
        "child_ages": child_ages,
        "wages": wages,
        "unemployment": unemployment,
        "interest": interest,
        "ssn": ssn,
        "claimed": claimed,
    }
    # Filers are 18 or older: the model makes a married 17-year-old a
    # dependent, not a spouse. The YAML cases cover age 17.
    for head_age in (18, 19, 22, 23, 24, 25, 30, 66)
    for head_student in (False, True)
    for spouse_h in (None, spouse(18), spouse(22, True, 2_000), spouse(30), spouse(70))
    for child_ages in ([], [5])
    for wages, unemployment, interest in (
        (0, 0, 0),
        (5_000, 0, 0),
        (5_000, 0, 20_000),
        (12_000, 8_000, 0),
    )
    for ssn, claimed in ((True, False), (False, False), (True, True))
]


def test_grid_invariants_2021():
    r, twin = check(GRID, 2021)
    cohort = r["me_childless_eitc_age_eligible"]
    # The grid reaches the 2021 students aged 19 to 23 whom main left out:
    # single, in the cohort and paid the pro forma credit.
    fixed = np.array(
        [
            h["spouse"] is None and h["head_student"] and 19 <= h["head_age"] <= 23
            for h in GRID
        ]
    )
    assert (fixed & cohort & (r["me_eitc"] > 0)).any()
    # Their credit equals the federally eligible twin's, which is positive.
    paid = fixed & cohort & (r["me_eitc"] > 0)
    np.testing.assert_allclose(r["me_eitc"][paid], twin["me_eitc"][paid], atol=0.01)


def test_grid_invariants_2025():
    r, _ = check(GRID, 2025)
    cohort = r["me_childless_eitc_age_eligible"]
    # Couples where one spouse meets the federal age test take the federal
    # path, and couples where neither does take the pro forma.
    head_in_range = np.array([18 <= h["head_age"] <= 24 for h in GRID])
    spouse_age = np.array(
        [-1 if h["spouse"] is None else h["spouse"]["age"] for h in GRID]
    )
    assert (head_in_range & (spouse_age == 30) & ~cohort & (r["eitc"] > 0)).any()
    assert (head_in_range & (spouse_age == 70) & cohort & (r["me_eitc"] > 0)).any()


def test_grid_invariants_2020_and_2026():
    for year in (2020, 2026):
        check(GRID, year)
