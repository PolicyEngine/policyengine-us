"""Invariants for state EITCs that recompute or replace the federal credit.

Maryland (Md. Code Tax-Gen. 10-704(c)(3)) and Maine (36 M.R.S. 5219-S(5)-(6))
recompute the federal EITC for childless filers without the federal minimum
age. New Jersey (P.L. 2021, c.130, section 1a(4)) pays 40% of the federal
childless maximum to a childless filer at least 18 who is ineligible for the
federal credit "due to age requirements" and meets "all qualifications,
except for the minimum or maximum age". None of them waives 26 U.S.C.
32(c)(1)(C), which denies the credit to anyone who claims the benefits of
section 911.

Each batch mixes households in the three states, with and without children,
across ages on both sides of the federal age limits, earnings and unemployment
compensation on both sides of the phase-out, SSN status, take-up and section
911 exclusions. The Hypothesis version is in
test_state_eitc_federal_qualifications_property.py.
"""

import numpy as np

from policyengine_us import Simulation

STATES = ("NJ", "MD", "ME")

TAX_UNIT_OUTPUTS = [
    "eitc",
    "eitc_eligible",
    "eitc_child_count",
    "eitc_phased_in",
    "eitc_maximum",
    "eitc_reduction",
    "filer_meets_eitc_identification_requirements",
    "nj_eitc",
    "nj_childless_eitc_age_eligible",
    "federal_eitc_without_age_minimum",
    "md_eitc",
    "me_pro_forma_childless_eitc",
    "me_eitc",
]


def build_situation(households, year):
    people, tax_units, marital_units = {}, {}, {}
    groups = {"households": {}, "spm_units": {}, "families": {}}
    for i, h in enumerate(households):
        head = f"head_{i}"
        people[head] = {
            "age": {year: h["head_age"]},
            "employment_income": {year: h["wages"]},
            "unemployment_compensation": {year: h["unemployment"]},
            "is_full_time_student": {year: h["student"]},
            "ssn_card_type": {year: "CITIZEN" if h["ssn"] else "OTHER_NON_CITIZEN"},
        }
        members = [head]
        marital_units[f"marital_unit_{i}"] = {"members": [head]}
        if h["spouse_age"] is not None:
            spouse = f"spouse_{i}"
            people[spouse] = {"age": {year: h["spouse_age"]}}
            members.append(spouse)
            marital_units[f"marital_unit_{i}"]["members"].append(spouse)
        for j, age in enumerate(h["child_ages"]):
            child = f"child_{i}_{j}"
            people[child] = {"age": {year: age}}
            members.append(child)
            marital_units[f"marital_unit_{i}_{j}"] = {"members": [child]}
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            "foreign_earned_income_exclusion": {year: h["exclusion"]},
            "takes_up_eitc": {year: h["takes_up"]},
        }
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: h["state"]},
        }
        groups["spm_units"][f"spm_unit_{i}"] = {"members": members}
        groups["families"][f"family_{i}"] = {"members": members}
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        **groups,
    }


def meets_federal_age(h, year):
    """Whether the head or spouse meets the federal childless age range."""
    if year == 2021:
        minimum, student_minimum, maximum = 19, 24, np.inf
    else:
        minimum, student_minimum, maximum = 25, 25, 64
    head_minimum = student_minimum if h["student"] else minimum
    if head_minimum <= h["head_age"] <= maximum:
        return True
    # The spouse is never a full-time student in these households.
    spouse = h["spouse_age"]
    return spouse is not None and minimum <= spouse <= maximum


def calculate(households, year):
    simulation = Simulation(situation=build_situation(households, year))
    return {v: np.asarray(simulation.calculate(v, year)) for v in TAX_UNIT_OUTPUTS}


def assert_invariants(households, year, r):
    # Model outputs are float32, so comparisons allow a cent.
    tol = 0.01
    state = np.array([h["state"] for h in households])
    nj, md, me = (state == s for s in STATES)
    excludes = np.array([h["exclusion"] > 0 for h in households])
    childless = r["eitc_child_count"] == 0
    federal_age = np.array([meets_federal_age(h, year) for h in households])
    nj_match = 0.4
    childless_maximum = r["eitc_maximum"][childless].max() if childless.any() else 0

    # Section 32(c)(1)(C): a section 911 claimant gets no federal credit and
    # no credit from any of the three states, with or without children.
    assert (r["eitc"][excludes] == 0).all()
    assert not r["nj_childless_eitc_age_eligible"][excludes].any()
    for v in ["nj_eitc", "federal_eitc_without_age_minimum", "md_eitc"]:
        assert (r[v][excludes] == 0).all(), v
    for v in ["me_pro_forma_childless_eitc", "me_eitc"]:
        assert (r[v][excludes] == 0).all(), v

    # New Jersey's two paths never overlap: the age path is only for filers
    # the federal credit turns away because of age.
    age_path = r["nj_childless_eitc_age_eligible"]
    assert not (age_path & r["eitc_eligible"]).any()
    assert not (age_path & (r["eitc"] > 0)).any()
    assert not (age_path & federal_age).any()
    assert not (age_path & ~childless).any()
    assert not (age_path & ~r["filer_meets_eitc_identification_requirements"]).any()
    # A federally eligible filer gets exactly 40% of the federal credit,
    # whatever its size, and nothing else.
    eligible = nj & r["eitc_eligible"]
    np.testing.assert_allclose(
        r["nj_eitc"][eligible], nj_match * r["eitc"][eligible], atol=tol
    )
    # A New Jersey filer who meets the federal age test, or has a qualifying
    # child, gets 40% of the federal credit and never the age-path amount.
    federal_only = nj & (federal_age | ~childless)
    np.testing.assert_allclose(
        r["nj_eitc"][federal_only], nj_match * r["eitc"][federal_only], atol=tol
    )
    # Otherwise the credit is 40% of the childless maximum or nothing.
    rest = nj & ~eligible
    paid = r["nj_eitc"][rest]
    assert np.all(
        np.isclose(paid, 0, atol=tol)
        | np.isclose(paid, nj_match * childless_maximum, atol=tol)
    ), paid
    # The age path pays only when a federal credit recomputed without the age
    # test would be positive (the federal earned income and AGI limits).
    pro_forma = np.minimum(
        r["eitc_phased_in"],
        np.maximum(0, r["eitc_maximum"] - r["eitc_reduction"]),
    )
    assert not (nj & (r["nj_eitc"] > 0) & ~r["eitc_eligible"] & (pro_forma <= 0)).any()
    assert (r["nj_eitc"] >= 0).all()

    # Maryland's pro forma is the federal computation without the minimum
    # age: for a federally eligible filer it is never below the federal
    # credit, and equals it whenever the federal credit is paid (take-up and
    # filing only ever zero the federal credit).
    md_eligible = md & r["eitc_eligible"]
    assert (
        r["federal_eitc_without_age_minimum"][md_eligible]
        >= r["eitc"][md_eligible] - tol
    ).all()
    paid_federally = md_eligible & (r["eitc"] > 0)
    np.testing.assert_allclose(
        r["federal_eitc_without_age_minimum"][paid_federally],
        r["eitc"][paid_federally],
        atol=tol,
    )
    # Both pro formas are bounded by the federal computation's own terms.
    for v, mask in [
        ("federal_eitc_without_age_minimum", md),
        ("me_pro_forma_childless_eitc", me),
    ]:
        assert (r[v][mask] >= 0).all(), v
        assert (r[v][mask] <= pro_forma[mask] + tol).all(), v
    # The pro formas exist only in their own state.
    assert (r["federal_eitc_without_age_minimum"][~md] == 0).all()
    assert (r["me_pro_forma_childless_eitc"][~me] == 0).all()
    assert (r["nj_eitc"][~nj] == 0).all()


def check(households, year=2025):
    r = calculate(households, year)
    assert_invariants(households, year, r)
    return r


GRID = [
    {
        "state": state,
        "head_age": head_age,
        "spouse_age": spouse_age,
        "child_ages": child_ages,
        "student": student,
        "wages": wages,
        "unemployment": unemployment,
        "exclusion": exclusion,
        "ssn": ssn,
        "takes_up": takes_up,
    }
    for state in STATES
    for head_age, spouse_age, student in (
        (20, None, False),
        (24, None, True),
        (40, None, False),
        (70, None, False),
        (20, 30, False),
        (20, 21, False),
    )
    for child_ages in ([], [5])
    for wages, unemployment in (
        (0, 0),
        (1_000, 0),
        (1_000, 12_000),
        (8_000, 0),
        (30_000, 0),
    )
    for exclusion in (0, 30_000)
    for ssn, takes_up in ((True, True), (False, True), (True, False))
]


def test_grid_invariants():
    r = check(GRID)
    state = np.array([h["state"] for h in GRID])
    excludes = np.array([h["exclusion"] > 0 for h in GRID])
    # The grid reaches the cases each rule changes.
    twin = [GRID.index({**h, "exclusion": 0}) for h in GRID]
    for v in ["federal_eitc_without_age_minimum", "me_pro_forma_childless_eitc"]:
        # Section 911 claimants whose twin without the exclusion is paid.
        assert (excludes & (r[v][twin] > 0)).any(), v
    nj = state == "NJ"
    # New Jersey age-path payments, and federal payments where the phase-out
    # reduction exceeds the phase-in amount.
    assert (nj & r["nj_childless_eitc_age_eligible"] & (r["nj_eitc"] > 0)).any()
    assert (nj & (r["eitc"] > 0) & (r["eitc_reduction"] > r["eitc_phased_in"])).any()


def test_grid_invariants_2021():
    # In 2021 the federal childless minimum age was 19 (24 for students) and
    # there was no maximum (26 U.S.C. 32(n), as added by ARPA section 9621).
    check(GRID, 2021)
