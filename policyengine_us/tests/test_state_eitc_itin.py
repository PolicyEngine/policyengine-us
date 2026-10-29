"""Invariants for the Maryland and Maine EITC waivers of 26 U.S.C. 32(m).

Section 32(m) confines the taxpayer identification number that 32(c)(1)(E)
(filer and spouse) and 32(c)(3)(D) (qualifying children) require to a Social
Security number valid for employment. Maryland computes its state and local
credits "without regard to the limitation under § 32(m)" from tax year 2020
(Md. Code Tax-Gen. 10-704(c) and (d); Chapter 40 of 2021). Maine accepts an
ITIN or any Social Security number from tax year 2021 "for an individual who
files a federal income tax return" (36 M.R.S. 5219-S(7)). Neither waives
32(c)(1)(C), the bar on section 911 claimants.

Every household runs beside a twin in which each member with an ITIN or a
Social Security number not valid for employment holds one valid for
employment instead. Identification types: SSN (citizen), ITIN (ssn_card_type
NONE, has_tin true), NONWORK (a Social Security number not valid for
employment) and NOTIN (no taxpayer identification number, kept in the twin).
A household's "files" sets its filing inputs (FILING_INPUTS): true keeps the
defaults, so it files to claim a refundable credit; "voluntarily" files
voluntarily and not for a credit; false files a federal return only if
required to.
The Hypothesis version is in test_state_eitc_itin_property.py.
"""

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.system import system
from policyengine_us.tools.state_eitc_helpers import SSN_LIMITATION_WAIVED_BRANCH

STATES = ("MD", "ME", "NJ")
ID_TYPES = ("SSN", "ITIN", "NONWORK", "NOTIN")
# First tax year of each state's waiver.
WAIVER_START = {"MD": 2020, "ME": 2021}
FILING_INPUTS = {
    True: {},
    "voluntarily": {
        "would_file_taxes_voluntarily": True,
        "would_file_if_eligible_for_refundable_credit": False,
    },
    False: {
        "would_file_taxes_voluntarily": False,
        "would_file_if_eligible_for_refundable_credit": False,
    },
}

TAX_UNIT_OUTPUTS = [
    "eitc",
    "eitc_child_count",
    "md_eitc_child_count",
    "md_federal_eitc_without_ssn_requirement",
    "federal_eitc_without_age_minimum",
    "md_eitc",
    "md_local_eitc",
    "me_eitc_child_count",
    "me_federal_eitc_without_ssn_requirement",
    "me_pro_forma_childless_eitc",
    "me_eitc",
    "me_childless_eitc_age_eligible",
]
FEDERAL_OUTPUTS = ["eitc", "eitc_child_count"]
REFERENCE_OUTPUTS = FEDERAL_OUTPUTS + [
    "federal_eitc_without_age_minimum",
    "me_pro_forma_childless_eitc",
]
STATE_OUTPUTS = [v for v in TAX_UNIT_OUTPUTS if v not in FEDERAL_OUTPUTS]
MD_CREDITS = [
    "md_federal_eitc_without_ssn_requirement",
    "federal_eitc_without_age_minimum",
    "md_eitc",
    "md_local_eitc",
]
ME_CREDITS = [
    "me_federal_eitc_without_ssn_requirement",
    "me_pro_forma_childless_eitc",
    "me_eitc",
]

# Structural reforms of the federal EITC. Each changes either the EITC's
# components (eitc_maximum, phase-in and phase-out rates) or the final eitc
# formula (the individual EITC's AGI limit; the End Child Poverty Act
# neutralizes eitc), and the state credits must follow them for ITIN
# households as for their SSN twins. The $10,000 limit falls inside the
# childless credit's range, so the childless pro formas
# (federal_eitc_without_age_minimum, me_pro_forma_childless_eitc), which
# evaluate the final eitc, must apply it too.
FOREVER = "2000-01-01.2100-12-31"
EITC_REFORMS = {
    "streamlined": {"gov.contrib.streamlined_eitc.in_effect": {FOREVER: True}},
    "individual_agi_limit": {
        "gov.contrib.individual_eitc.in_effect": {FOREVER: True},
        "gov.contrib.individual_eitc.agi_eitc_limit": {FOREVER: 10_000},
    },
    "halve_joint_phase_out": {"gov.contrib.joint_eitc.in_effect": {FOREVER: True}},
    "working_parents": {
        "gov.contrib.congress.mcdonald_rivet.working_parents_tax_relief_act.in_effect": {
            FOREVER: True
        }
    },
    "family_security_act": {
        "gov.contrib.congress.romney.family_security_act_2_0.eitc.apply_eitc_structure": {
            FOREVER: True
        }
    },
    "end_child_poverty_act": {
        "gov.contrib.congress.tlaib.end_child_poverty_act.in_effect": {FOREVER: True}
    },
}

PERSON_INPUTS = {
    "SSN": {"ssn_card_type": "CITIZEN", "has_tin": True},
    "ITIN": {"ssn_card_type": "NONE", "has_tin": True},
    "NONWORK": {"ssn_card_type": "OTHER_NON_CITIZEN", "has_tin": True},
    "NOTIN": {"ssn_card_type": "NONE", "has_tin": False},
}


def person(age, id_type, year, **extra):
    inputs = {k: {year: v} for k, v in PERSON_INPUTS[id_type].items()}
    return {"age": {year: age}, **inputs, **{k: {year: v} for k, v in extra.items()}}


def to_ssn(id_type):
    return "SSN" if id_type in ("ITIN", "NONWORK") else id_type


def ssn_twin(h):
    """The same household with each ITIN or NONWORK number made a valid SSN."""
    return {
        **h,
        "head_id": to_ssn(h["head_id"]),
        "spouse_id": None if h["spouse_id"] is None else to_ssn(h["spouse_id"]),
        "child_ids": [to_ssn(c) for c in h["child_ids"]],
    }


def build_situation(households, year, waived=None, tax_unit_inputs=None):
    """The households as a situation.

    `waived`, a list of booleans, sets eitc_ssn_limitation_waived by input:
    for those tax units the EITC's identification test accepts any TIN.
    `tax_unit_inputs` maps a tax unit variable to a value for each household,
    after (and over) the filing inputs of households that don't file.
    """
    people, tax_units, marital_units = {}, {}, {}
    groups = {"households": {}, "spm_units": {}, "families": {}}
    for i, h in enumerate(households):
        head = f"head_{i}"
        people[head] = person(
            h["head_age"], h["head_id"], year, employment_income=h["wages"]
        )
        members = [head]
        marital_units[f"marital_unit_{i}"] = {"members": [head]}
        if h["spouse_id"] is not None:
            spouse = f"spouse_{i}"
            people[spouse] = person(h["spouse_age"], h["spouse_id"], year)
            members.append(spouse)
            marital_units[f"marital_unit_{i}"]["members"].append(spouse)
        for j, id_type in enumerate(h["child_ids"]):
            child = f"child_{i}_{j}"
            people[child] = person(3 + 4 * j, id_type, year)
            members.append(child)
            marital_units[f"marital_unit_{i}_{j}"] = {"members": [child]}
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            "foreign_earned_income_exclusion": {year: h["exclusion"]},
            "takes_up_eitc": {year: h["takes_up"]},
        }
        for variable, value in FILING_INPUTS[h.get("files", True)].items():
            tax_units[f"tax_unit_{i}"][variable] = {year: value}
        if waived is not None:
            tax_units[f"tax_unit_{i}"]["eitc_ssn_limitation_waived"] = {
                year: bool(waived[i])
            }
        for variable, values in (tax_unit_inputs or {}).items():
            value = values[i].item() if hasattr(values[i], "item") else values[i]
            tax_units[f"tax_unit_{i}"][variable] = {year: value}
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


def filer_ids(h):
    return [h["head_id"]] + ([] if h["spouse_id"] is None else [h["spouse_id"]])


def waiver_applies(h, year, files):
    """Whether the household's state waives 32(m) for it.

    `files`: whether the household files a federal return (required to, or
    by its filing inputs). Maine's waiver reaches only a filer who files one.
    """
    started = year >= WAIVER_START.get(h["state"], np.inf)
    return started and (h["state"] != "ME" or files)


def accepted_ids(h, year, files):
    if waiver_applies(h, year, files):
        return {"SSN", "ITIN", "NONWORK"}
    return {"SSN"}


def pro_forma_eligible(h, year, files):
    """The pro formas' eligibility, from the household's description.

    The filer's and spouse's identification (any TIN once the state's waiver
    applies to the household) and the section 911 bar. In Maryland, also the
    federal maximum age, which a qualifying child (one with an accepted TIN)
    lifts; Maine's pro forma covers only its 18-24 cohort, so the cohort test
    stands in for it. The households have no investment income and no
    dependent filer, so the other conditions hold.
    """
    accepted = accepted_ids(h, year, files)
    eligible = set(filer_ids(h)) <= accepted and h["exclusion"] == 0
    if h["state"] == "MD":
        max_age = system.parameters(year).gov.irs.credits.eitc.eligibility.age.max
        ages = [h["head_age"]] + ([] if h["spouse_id"] is None else [h["spouse_age"]])
        has_child = any(c in accepted for c in h["child_ids"])
        eligible = eligible and (has_child or min(ages) <= max_age)
    return eligible


def calculate(households, year, reform=None, federal_first=True):
    """Run the households and their SSN twins; twin[i] indexes i's twin.

    With federal_first false, the state credits are calculated before the
    federal ones. Either way the federal values must be what they would be
    without the state credits: read again afterwards, they match copies
    taken before. The third result holds two references, each the
    households alone in a fresh simulation, with each household's AGI as
    calculated by input (the AGI of the return as filed) and
    eitc_ssn_limitation_waived by input wherever the household's state
    waives 32(m) for it: the reference's federal variables, and "pro_forma",
    the federal eitc with eitc_eligible set from the household's description
    (pro_forma_eligible) and with take-up and filing by input. It also holds
    "files": whether each household files a federal return, from its
    description and the federal filing requirement.
    """
    n = len(households)
    combined = list(households) + [ssn_twin(h) for h in households]
    simulation = Simulation(
        situation=build_situation(combined, year), reform=EITC_REFORMS.get(reform)
    )
    identified = np.array(
        simulation.calculate("meets_eitc_identification_requirements", year)
    )
    order = (
        FEDERAL_OUTPUTS + STATE_OUTPUTS
        if federal_first
        else STATE_OUTPUTS + FEDERAL_OUTPUTS
    )
    r = {v: np.array(simulation.calculate(v, year)) for v in order}
    np.testing.assert_array_equal(
        simulation.calculate("meets_eitc_identification_requirements", year),
        identified,
    )
    for v in FEDERAL_OUTPUTS:
        np.testing.assert_array_equal(simulation.calculate(v, year), r[v], err_msg=v)
    agi = np.array(simulation.calculate("adjusted_gross_income", year))[:n]
    required = np.array(simulation.calculate("tax_unit_is_required_to_file", year))
    files = [
        bool(h.get("files", True)) or bool(required[i])
        for i, h in enumerate(households)
    ]
    waived = [waiver_applies(h, year, f) for h, f in zip(households, files)]
    relaxed = Simulation(
        situation=build_situation(
            households, year, waived, {"adjusted_gross_income": agi}
        ),
        reform=EITC_REFORMS.get(reform),
    )
    reference = {v: np.array(relaxed.calculate(v, year)) for v in REFERENCE_OUTPUTS}
    ones = [True] * n
    pro_forma = Simulation(
        situation=build_situation(
            households,
            year,
            waived,
            {
                "adjusted_gross_income": agi,
                "eitc_eligible": [
                    pro_forma_eligible(h, year, f) for h, f in zip(households, files)
                ],
                "takes_up_eitc": ones,
                "would_file_taxes_voluntarily": ones,
            },
        ),
        reform=EITC_REFORMS.get(reform),
    )
    reference["pro_forma"] = np.array(pro_forma.calculate("eitc", year))
    reference["files"] = np.array(files)
    return (
        {v: x[:n] for v, x in r.items()},
        {v: x[n:] for v, x in r.items()},
        reference,
    )


def assert_invariants(households, year, r, t, reference, reform=None):
    # Model outputs are float32, so comparisons allow a cent.
    tol = 0.01
    state = np.array([h["state"] for h in households])
    md, me = state == "MD", state == "ME"
    files = reference["files"]
    # Whether the household's state waives 32(m) for it: Maryland from 2020;
    # Maine from 2021, for a filer who files a federal return.
    applies = np.array([waiver_applies(h, year, f) for h, f in zip(households, files)])
    excludes = np.array([h["exclusion"] > 0 for h in households])
    filer_without_tin = np.array(["NOTIN" in filer_ids(h) for h in households])
    all_valid_ssn = np.array(
        [set(filer_ids(h) + h["child_ids"]) <= {"SSN"} for h in households]
    )
    takes_up = np.array([h["takes_up"] for h in households])

    # Section 32(c)(1)(C): a section 911 claimant gets nothing on any path,
    # whatever the identification of the filer, spouse and children.
    for v in MD_CREDITS + ME_CREDITS:
        assert (r[v][excludes] == 0).all(), v

    # The credits exist only in their own state.
    for v in MD_CREDITS + ["md_eitc_child_count"]:
        assert (r[v][~md] == 0).all(), v
    for v in ME_CREDITS + ["me_eitc_child_count"]:
        assert (r[v][~me] == 0).all(), v

    # Every path still requires a taxpayer identification number for the
    # filer and spouse (32(c)(1)(E)); only its kind is waived.
    for v in MD_CREDITS + ME_CREDITS:
        assert (r[v][filer_without_tin] == 0).all(), v

    # Child counts: the waiver counts qualifying children with any TIN.
    for s, count in [("MD", "md_eitc_child_count"), ("ME", "me_eitc_child_count")]:
        mask = state == s
        expected = np.array(
            [
                sum(c in accepted_ids(h, year, f) for c in h["child_ids"])
                for h, f in zip(households, files)
            ]
        )
        np.testing.assert_array_equal(r[count][mask], expected[mask], err_msg=count)
        assert (r[count][mask] >= r["eitc_child_count"][mask]).all(), count

    # The 32(m)-free credit is the federal credit when no one needs the
    # waiver (a differential check of the branch against the federal
    # variables) or the waiver doesn't apply to the household (before it,
    # or in Maine without a federal return). Under current law it is never below the
    # federal credit, since an added qualifying child never lowers the
    # federal amount. Some reforms break that (the streamlined EITC at
    # $30,000 of wages, with a second child), and the state credit then
    # follows the reform's amount with the child, as the SSN twin's federal
    # credit does.
    for s, basis in [
        ("MD", "md_federal_eitc_without_ssn_requirement"),
        ("ME", "me_federal_eitc_without_ssn_requirement"),
    ]:
        mask = state == s
        if reform is None:
            assert (r[basis][mask] >= r["eitc"][mask] - tol).all(), basis
        same = mask & (all_valid_ssn | ~applies)
        np.testing.assert_allclose(r[basis][same], r["eitc"][same], atol=tol)

    # The 32(m)-free variables are those of the reference, a fresh
    # simulation where the EITC's identification test accepts any TIN by
    # input wherever the waiver applies to the household and AGI is that of
    # the return as filed: the waivers' definition, and a differential check
    # of the branch. Where the waiver doesn't apply (before it starts, or a
    # Maine household that files no federal return), the reference's
    # identification test is the federal one. Unlike the twin, the reference
    # also holds where another SSN rule changes the household's taxes (the
    # education-credit test below; the recovery rebate credit cases in
    # state_eitc_itin_return_as_filed.yaml).
    for s, basis, count, pro_forma in [
        (
            "MD",
            "md_federal_eitc_without_ssn_requirement",
            "md_eitc_child_count",
            "federal_eitc_without_age_minimum",
        ),
        (
            "ME",
            "me_federal_eitc_without_ssn_requirement",
            "me_eitc_child_count",
            "me_pro_forma_childless_eitc",
        ),
    ]:
        mask = state == s
        np.testing.assert_allclose(
            r[basis][mask], reference["eitc"][mask], atol=tol, err_msg=basis
        )
        np.testing.assert_array_equal(
            r[count][mask], reference["eitc_child_count"][mask], err_msg=count
        )
        np.testing.assert_allclose(
            r[pro_forma][mask],
            reference[pro_forma][mask],
            atol=tol,
            err_msg=pro_forma,
        )

    # The childless pro formas are the final federal eitc, reforms included,
    # with eitc_eligible set to their own conditions and no take-up or
    # filing condition: the "pro_forma" reference, evaluated with those
    # conditions written out from each household's description. Maine's is
    # defined for its childless cohort only (me_childless_eitc_age_eligible,
    # whose own tests cover the ages; the child count it reads is checked
    # above).
    me_cohort = r["me_childless_eitc_age_eligible"]
    np.testing.assert_allclose(
        r["federal_eitc_without_age_minimum"][md],
        reference["pro_forma"][md],
        atol=tol,
        err_msg="federal_eitc_without_age_minimum",
    )
    np.testing.assert_allclose(
        r["me_pro_forma_childless_eitc"][me],
        np.where(me_cohort, reference["pro_forma"], 0)[me],
        atol=tol,
        err_msg="me_pro_forma_childless_eitc",
    )

    # Where the waiver applies, an ITIN or NONWORK number is treated exactly
    # like a valid SSN: every variable matches the twin's, in Maryland for
    # nonfilers too. The generated households have no income or expenses
    # that another SSN rule reaches. Where it doesn't (before it starts, or
    # a Maine household without a federal return), the final credit never
    # exceeds the twin's (an intermediate pro forma can, since a child
    # without a valid SSN moves the filer to the childless path). That bound
    # holds for households that take up the EITC and file; for others it can
    # fail on main too, because the childless pro formas
    # (federal_eitc_without_age_minimum, me_pro_forma_childless_eitc) apply no
    # take-up or filing condition while the with-child paths follow the
    # federal credit's. Like the bound above, it relies on an added child
    # never lowering the federal amount, so it is checked under current law
    # only.
    for s, credits, final in [
        ("MD", MD_CREDITS, ["md_eitc", "md_local_eitc"]),
        ("ME", ME_CREDITS, ["me_eitc"]),
    ]:
        mask = state == s
        for v in credits:
            np.testing.assert_allclose(
                r[v][mask & applies], t[v][mask & applies], atol=tol, err_msg=v
            )
        if reform is None:
            bound = mask & ~applies & takes_up & files
            for v in final:
                assert (r[v][bound] <= t[v][bound] + tol).all(), v

    for v in MD_CREDITS + ME_CREDITS:
        assert (r[v] >= 0).all(), v

    # The federal credit itself keeps 32(m): a filer or spouse without a
    # valid SSN gets none, whatever the state credits do.
    if reform is None:
        lacks_valid_ssn = np.array([set(filer_ids(h)) != {"SSN"} for h in households])
        assert (r["eitc"][lacks_valid_ssn] == 0).all()


def check(households, year=2025, reform=None, federal_first=True):
    r, t, reference = calculate(households, year, reform, federal_first)
    assert_invariants(households, year, r, t, reference, reform)
    return r, t


GRID = [
    {
        "state": state,
        "head_age": head_age,
        "spouse_age": 35,
        "head_id": head_id,
        "spouse_id": spouse_id,
        "child_ids": child_ids,
        "wages": wages,
        "exclusion": exclusion,
        "takes_up": takes_up,
        "files": files,
    }
    for state in STATES
    for head_age in (20, 35)
    for head_id in ID_TYPES
    for spouse_id in (None, "SSN", "ITIN", "NOTIN")
    for child_ids in ([], ["SSN"], ["ITIN"], ["NOTIN"], ["SSN", "ITIN"])
    # $10,000 of wages doesn't require a return, so "files" decides. The
    # take-up row files voluntarily, so each way of filing meets Maine's
    # condition somewhere.
    for wages, exclusion, takes_up, files in (
        (10_000, 0, True, True),
        (30_000, 0, True, True),
        (10_000, 30_000, True, True),
        (10_000, 0, False, "voluntarily"),
        (10_000, 0, True, False),
    )
]


def test_grid_invariants():
    # The state credits first; the year tests below take the federal first.
    r, t = check(GRID, federal_first=False)
    state = np.array([h["state"] for h in GRID])
    itin_filer = np.array(["ITIN" in filer_ids(h) for h in GRID])
    itin_child = np.array(["ITIN" in h["child_ids"] for h in GRID])
    # The grid reaches the cases the waiver changes: ITIN filers paid by
    # each state with no federal credit, and ITIN children that raise the
    # amount above the federal one.
    for s, v in [("MD", "md_eitc"), ("ME", "me_eitc")]:
        mask = state == s
        assert (mask & itin_filer & (r["eitc"] == 0) & (r[v] > 0)).any(), v
    for s, basis in [
        ("MD", "md_federal_eitc_without_ssn_requirement"),
        ("ME", "me_federal_eitc_without_ssn_requirement"),
    ]:
        mask = state == s
        assert (mask & itin_child & (r[basis] > r["eitc"] + 1)).any(), basis
    # And the households Maine's filing condition separates: an ITIN filer
    # with no federal return gets no Maine credit where the SSN twin, under
    # the childless pro forma's own convention, gets one. Maryland, with no
    # such condition, pays the same ITIN nonfiler as the twin.
    nonfiler = np.array([not h["files"] for h in GRID])
    me_cut = (state == "ME") & itin_filer & nonfiler & (r["me_eitc"] == 0)
    assert (me_cut & (t["me_eitc"] > 0)).any()
    md_paid = (state == "MD") & itin_filer & nonfiler & (r["eitc"] == 0)
    assert (md_paid & (r["md_eitc"] > 0)).any()
    # A voluntary filer with an ITIN, filing for no credit, meets it.
    voluntary = np.array([h["files"] == "voluntarily" for h in GRID])
    assert ((state == "ME") & itin_filer & voluntary & (r["me_eitc"] > 0)).any()


def test_grid_invariants_before_and_at_the_waivers():
    # 2019: neither state waives 32(m). 2020: Maryland only. 2021: both,
    # under the ARPA childless parameters.
    for year in (2019, 2020, 2021):
        check(GRID, year)


# A smaller grid per reform: the states with a waiver, adults of both pro
# forma age groups, and incomes on the phase-in, plateau and phase-out.
REFORM_GRID = [
    {
        "state": state,
        "head_age": head_age,
        "spouse_age": 35,
        "head_id": head_id,
        "spouse_id": spouse_id,
        "child_ids": child_ids,
        "wages": wages,
        "exclusion": 0,
        "takes_up": True,
    }
    for state in ("MD", "ME")
    for head_age in (20, 35)
    for head_id in ("SSN", "ITIN")
    for spouse_id in (None, "ITIN")
    for child_ids in ([], ["SSN"], ["ITIN"], ["SSN", "ITIN"])
    for wages in (5_000, 15_000, 30_000)
]


def merge_years(a, b):
    """Merge two situations for the same households built for different years."""
    if not isinstance(a, dict):
        return a
    return {**b, **{k: merge_years(v, b[k]) if k in b else v for k, v in a.items()}}


def test_one_simulation_across_the_waiver_start_years():
    # The waived branch serves one period. A simulation that calculates
    # 2019 (no waiver), 2025 (both) and then 2020 (Maryland only) matches a
    # simulation that calculates each year alone.
    years = (2019, 2025, 2020)
    situation = build_situation(REFORM_GRID, years[0])
    for year in years[1:]:
        situation = merge_years(situation, build_situation(REFORM_GRID, year))
    simulation = Simulation(situation=situation)
    for year in years:
        alone = Simulation(situation=build_situation(REFORM_GRID, year))
        for v in TAX_UNIT_OUTPUTS:
            np.testing.assert_allclose(
                simulation.calculate(v, year),
                alone.calculate(v, year),
                atol=0.01,
                err_msg=f"{v} {year}",
            )


def test_a_later_period_reads_its_own_inputs():
    # Sol's r4 case for the branch's per-period creation: the 2025 wage input
    # changes after the 2020 branch exists. A branch kept from 2020 would
    # still hold the old $5,000 (its copy of the inputs), while the AGI it
    # takes as filed is $10,000; the 2025 branch, created from the parent as
    # it stands then, reads $10,000, as a simulation of 2025 alone does.
    itin_parent = {
        "state": "MD",
        "head_age": 35,
        "spouse_age": 35,
        "head_id": "ITIN",
        "spouse_id": None,
        "child_ids": ["SSN"],
        "wages": 5_000,
        "exclusion": 0,
        "takes_up": True,
    }
    situation = merge_years(
        build_situation([itin_parent], 2020), build_situation([itin_parent], 2025)
    )
    simulation = Simulation(situation=situation)
    basis = "md_federal_eitc_without_ssn_requirement"
    assert simulation.calculate(basis, 2020)[0] > 0
    simulation.set_input("employment_income", 2025, np.array([10_000, 0]))
    alone = Simulation(
        situation=build_situation([{**itin_parent, "wages": 10_000}], 2025)
    )
    for v in (basis, "md_eitc"):
        np.testing.assert_allclose(
            simulation.calculate(v, 2025), alone.calculate(v, 2025), atol=0.01
        )
    # One child, $10,000: the phase-in at 34%.
    np.testing.assert_allclose(simulation.calculate(basis, 2025), 3_400, atol=0.01)


@pytest.fixture(scope="module")
def reform_grid_baseline():
    # Read-only arrays, shared by the reform cases below.
    return calculate(REFORM_GRID, 2025)[0]


@pytest.mark.parametrize("reform", sorted(EITC_REFORMS))
def test_grid_invariants_under_eitc_reforms(reform, reform_grid_baseline):
    r, t = check(REFORM_GRID, 2025, reform)
    # Each reform changes some credit, so the grid exercises it.
    baseline = reform_grid_baseline
    assert any(
        not np.allclose(r[v], baseline[v], atol=0.01)
        for v in ("md_federal_eitc_without_ssn_requirement", "me_eitc")
    ), reform


# Labor-supply responses. The waived branch takes each person's earnings
# after the response as they are, so the 32(m)-free credit is the federal
# formula on actual earnings with identification relaxed, whichever variable
# is calculated first. The reference is a fresh simulation with those
# earnings as input, the EITC's identification test relaxed by input, and no
# response.
LABOR_SUPPLY_REFORM = {
    **EITC_REFORMS["working_parents"],
    "gov.simulation.labor_supply_responses.elasticities.income": {FOREVER: -0.05},
    "gov.simulation.labor_supply_responses.elasticities.substitution.all": {
        FOREVER: 0.25
    },
}


def test_labor_supply_responses_in_either_order():
    year = 2025
    # An ITIN parent with an SSN child in each state, then their SSN twins.
    itin_parents = [
        {
            "state": state,
            "head_age": 35,
            "spouse_age": 35,
            "head_id": "ITIN",
            "spouse_id": None,
            "child_ids": ["SSN"],
            "wages": 5_000,
            "exclusion": 0,
            "takes_up": True,
        }
        for state in ("MD", "ME")
    ]
    households = itin_parents + [ssn_twin(h) for h in itin_parents]
    bases = [
        "md_federal_eitc_without_ssn_requirement",
        "me_federal_eitc_without_ssn_requirement",
    ]
    credits = ["md_eitc", "me_eitc"]
    # The filing requirement by input, as it is for these households. Maine's
    # waiver reads it on the parent, and calculating it there calculates the
    # responses, which a branch created afterwards inherits (core's
    # get_branch starts from the parent's cached values). By input, nothing
    # is cached when the branch is created, so the test needs
    # keep_return_as_filed to copy the responses (Sol r6).
    situation = build_situation(
        households,
        year,
        tax_unit_inputs={"tax_unit_is_required_to_file": [False] * len(households)},
    )
    heads = [list(situation["people"]).index(f"head_{i}") for i in range(4)]
    results = []
    for order in (["eitc"] + bases + credits, bases + credits + ["eitc"]):
        simulation = Simulation(situation=situation, reform=LABOR_SUPPLY_REFORM)
        result = {v: np.array(simulation.calculate(v, year)) for v in order}
        earnings = simulation.calculate("employment_income", year)
        result["earnings"] = np.array(earnings)[heads]
        results.append(result)
    for v in results[0]:
        np.testing.assert_allclose(results[0][v], results[1][v], atol=0.01, err_msg=v)
    result = results[0]
    # The ITIN parents respond, so the test reaches the response chain, and
    # get no federal credit.
    assert (abs(result["earnings"][:2] - 5_000) > 1).all()
    assert (result["eitc"][:2] == 0).all()
    reference_situation = build_situation(
        [
            {**h, "wages": float(earnings)}
            for h, earnings in zip(itin_parents, result["earnings"][:2])
        ],
        year,
        waived=[True, True],
    )
    reference = Simulation(
        situation=reference_situation, reform=EITC_REFORMS["working_parents"]
    )
    expected = reference.calculate("eitc", year)
    assert (expected > 0).all()
    for i, (basis, credit) in enumerate(zip(bases, credits)):
        np.testing.assert_allclose(result[basis][i], expected[i], atol=0.01)
        np.testing.assert_allclose(
            result[credit][i], reference.calculate(credit, year)[i], atol=0.01
        )


def test_other_ssn_rules_can_separate_the_twin_but_not_the_reference():
    # The reconciliation bill's SSN requirement for education credits keeps
    # an ITIN parent itemizing in 2020, while the SSN twin takes the standard
    # deduction and the $300 charitable deduction above the line, so their
    # AGIs and credits differ. Maryland's waiver relaxes 32(m) only, not that
    # rule, so the 32(m)-free credit is the reference's federal credit.
    year = 2020
    reform = {
        "gov.contrib.reconciliation.ssn_for_llc_and_aoc.in_effect": {FOREVER: True}
    }
    itin_parent = {
        "state": "MD",
        "head_age": 35,
        "spouse_age": 35,
        "head_id": "ITIN",
        "spouse_id": None,
        "child_ids": ["SSN"],
        "wages": 30_000,
        "exclusion": 0,
        "takes_up": True,
    }
    parent_inputs = {
        "taxable_interest_income": 3_000,
        "qualified_tuition_expenses": 4_000,
        "is_eligible_for_american_opportunity_credit": True,
        "deductible_mortgage_interest": 19_300,
        "charitable_cash_donations": 300,
    }

    def situation(households, *args):
        built = build_situation(households, year, *args)
        for i in range(len(households)):
            for k, v in parent_inputs.items():
                built["people"][f"head_{i}"][k] = {year: v}
            built["people"][f"child_{i}_0"]["age"] = {year: 17}
            built["tax_units"][f"tax_unit_{i}"][
                "capped_qualified_tuition_expenses_ald"
            ] = {year: 0}
        return built

    basis = "md_federal_eitc_without_ssn_requirement"
    simulation = Simulation(
        situation=situation([itin_parent, ssn_twin(itin_parent)]), reform=reform
    )
    result = simulation.calculate(basis, year)
    itemizes = simulation.calculate("tax_unit_itemizes", year)
    agi = simulation.calculate("adjusted_gross_income", year)
    relaxed = Simulation(
        situation=situation([itin_parent], [True], {"adjusted_gross_income": agi[:1]}),
        reform=reform,
    )
    assert itemizes[0] and not itemizes[1]
    assert result[0] < result[1] - 1
    np.testing.assert_allclose(result[0], relaxed.calculate("eitc", year)[0], atol=0.01)


def test_the_waived_branch_keeps_other_ssn_rules():
    # The 2020 recovery rebate credits require valid Social Security numbers
    # of their own (26 U.S.C. 6428(g), 6428A(g)). Maryland's waiver relaxes
    # the EITC's identification test only, so the branch the 32(m)-free
    # credit is calculated in, and the itemization branches it creates,
    # give an ITIN parent none of them, as the parent's own simulation does.
    year = 2020
    itin_parent = {
        "state": "MD",
        "head_age": 35,
        "spouse_age": 35,
        "head_id": "ITIN",
        "spouse_id": None,
        "child_ids": ["SSN"],
        "wages": 30_000,
        "exclusion": 0,
        "takes_up": True,
    }
    simulation = Simulation(situation=build_situation([itin_parent], year))
    basis = simulation.calculate("md_federal_eitc_without_ssn_requirement", year)
    assert simulation.calculate("eitc", year)[0] == 0
    assert basis[0] > 0
    branch = simulation.branches[SSN_LIMITATION_WAIVED_BRANCH]
    np.testing.assert_allclose(branch.calculate("eitc", year), basis)
    branch.calculate("tax_unit_itemizes", year)
    branches = [branch] + [
        branch.branches[name] for name in ("itemizing", "not_itemizing")
    ]
    for v in ("rrc_cares", "rrc_caa"):
        assert simulation.calculate(v, year)[0] == 0, v
        for b in branches:
            assert b.calculate(v, year)[0] == 0, (b.branch_name, v)
