"""Invariants for the section 911 bar on the refundable Child Tax Credit.

26 U.S.C. 24(d)(3): "Paragraph (1) shall not apply to any taxpayer for any
taxable year if such taxpayer elects to exclude any amount from gross income
under section 911 for such taxable year." The 2025 Schedule 8812
instructions (Part II-A) put it as "If you file Form 2555, you cannot claim
the additional child tax credit."

Each batch of households is computed twice: under current law and under a
reform that switches the bar off, which reproduces the formula without it.
Households live in Texas and take the standard deduction, so the CTC's
tax-liability limit equals the tax the model computes.

The model does not apply the section 911(f) rule that taxes included income
at the rates it would face if the excluded amount were added back (the Foreign
Earned Income Tax Worksheet). The tax identity below is a property of the
model's liability, not a worksheet result.

Section 32(c)(1)(C) also denies the EITC to a section 911 claimant, in every
year, so the EITC of a filer with an exclusion is zero under both runs.

The Hypothesis version of these checks is in
test_ctc_foreign_earned_income_exclusion_property.py, which skips without
the dev extra; the grid tests here always run.
"""

from functools import cache

import numpy as np
from policyengine_core.reforms import Reform

from policyengine_us import CountryTaxBenefitSystem, Simulation

BAR = "gov.irs.credits.ctc.refundable.foreign_earned_income_exclusion_bar_applies"


@cache
def no_bar_system():
    # One reformed system serves every household batch.
    reform = Reform.from_dict({BAR: {"2010-01-01.2100-12-31": False}}, country_id="us")
    return CountryTaxBenefitSystem(reform=reform)


OUTPUTS = [
    "tax_unit_itemizes",
    "foreign_earned_income_exclusion",
    "income_tax_before_credits",
    "ctc",
    "ctc_refundable_maximum",
    "refundable_ctc_barred_by_section_911_exclusion",
    "ctc_credit_limit_worksheet_b_applies",
    "refundable_ctc",
    "non_refundable_ctc",
    "income_tax_capped_non_refundable_credits",
    # No residence test in the formula, so it is computed for every household.
    "pr_refundable_ctc",
    "eitc",
    "income_tax",
]


def build_situation(households, year):
    people, tax_units, marital_units = {}, {}, {}
    groups = {"households": {}, "spm_units": {}, "families": {}}
    for i, h in enumerate(households):
        head = f"head_{i}"
        people[head] = {"age": {year: 40}, "employment_income": {year: h["wages"]}}
        members = [head]
        marital_units[f"marital_unit_{i}"] = {"members": [head]}
        if h["married"]:
            spouse = f"spouse_{i}"
            people[spouse] = {"age": {year: 40}}
            members.append(spouse)
            marital_units[f"marital_unit_{i}"]["members"].append(spouse)
        for j, age in enumerate(h["dependent_ages"]):
            dependent = f"dependent_{i}_{j}"
            people[dependent] = {"age": {year: age}}
            members.append(dependent)
            marital_units[f"marital_unit_{i}_{j}"] = {"members": [dependent]}
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            "foreign_earned_income_exclusion": {year: h["exclusion"]},
        }
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "TX"},
        }
        groups["spm_units"][f"spm_unit_{i}"] = {"members": members}
        groups["families"][f"family_{i}"] = {"members": members}
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        **groups,
    }


def calculate(households, year, bar=True):
    system = {} if bar else {"tax_benefit_system": no_bar_system()}
    simulation = Simulation(situation=build_situation(households, year), **system)
    return {v: np.asarray(simulation.calculate(v, year)) for v in OUTPUTS}


def assert_invariants(law, no_bar):
    tol = 0.01
    assert not law["tax_unit_itemizes"].any()
    excludes = law["foreign_earned_income_exclusion"] > 0
    barred = "refundable_ctc_barred_by_section_911_exclusion"
    # Section 24(d)(3): the bar is exactly the filers with an exclusion, and
    # none of them has a refundable CTC.
    assert np.array_equal(law[barred], excludes)
    assert not no_bar[barred].any()
    assert (law["refundable_ctc"][excludes] == 0).all()
    # The Puerto Rico credit's social security route is barred as well.
    assert (law["pr_refundable_ctc"][excludes] == 0).all()
    # Section 32(c)(1)(C): no EITC for a section 911 claimant, bar or not.
    assert (law["eitc"][excludes] == 0).all()
    assert (no_bar["eitc"][excludes] == 0).all()
    # Schedule 8812: a filer the bar denies the refund skips Credit Limit
    # Worksheet B. With the bar switched off, excluders complete it as other
    # filers do, so the bar is its only Form 2555 test.
    worksheet_b = "ctc_credit_limit_worksheet_b_applies"
    assert not (law[worksheet_b] & law[barred]).any()
    assert np.array_equal(law[worksheet_b], no_bar[worksheet_b] & ~law[barred])
    # Filers without the exclusion are untouched, bit for bit.
    for v in [
        "refundable_ctc",
        "non_refundable_ctc",
        "pr_refundable_ctc",
        "income_tax",
    ]:
        assert np.array_equal(law[v][~excludes], no_bar[v][~excludes]), v
    # The bar only ever removes refundable credit.
    assert (law["refundable_ctc"] <= no_bar["refundable_ctc"]).all()
    for r in [law, no_bar]:
        # True by the definition of non_refundable_ctc; kept as a guard on it.
        np.testing.assert_allclose(
            r["refundable_ctc"] + r["non_refundable_ctc"], r["ctc"], atol=tol
        )
        assert (r["refundable_ctc"] >= 0).all()
        assert (
            r["refundable_ctc"]
            <= np.minimum(r["ctc"], r["ctc_refundable_maximum"]) + tol
        ).all()
    # The CTC that offsets tax is the same either way: section 24(d)(1) refunds
    # only what tax could not absorb, so the section 26(a)-limited credits are
    # equal even though a barred filer's non-refundable CTC is the whole
    # credit. The bar therefore raises the tax by exactly the refund it denies.
    np.testing.assert_allclose(
        law["income_tax_capped_non_refundable_credits"],
        no_bar["income_tax_capped_non_refundable_credits"],
        atol=tol,
    )
    np.testing.assert_allclose(
        law["income_tax"] - no_bar["income_tax"],
        np.where(excludes, no_bar["refundable_ctc"], 0),
        atol=tol,
    )


def check(households, year=2025):
    law = calculate(households, year)
    no_bar = calculate(households, year, bar=False)
    assert_invariants(law, no_bar)
    return law, no_bar


GRID = [
    {
        "married": married,
        "dependent_ages": ages,
        "wages": wages,
        "exclusion": exclusion,
    }
    for married in (True, False)
    for ages in ([], [5], [5, 8], [3, 6, 9], [17], [5, 17])
    for wages in (0, 8_000, 30_000, 60_000, 120_000, 420_000)
    for exclusion in (0, 1, 50_000, 130_000)
]


def test_grid_invariants():
    law, no_bar = check(GRID)
    excludes = law["foreign_earned_income_exclusion"] > 0
    # The grid reaches filers whose refund the bar removes.
    assert (excludes & (no_bar["refundable_ctc"] > 0)).any()


def test_bar_applies_from_2015_but_not_in_2021():
    # In 2021, section 24(i)(1)(A) switched off all of subsection (d) for
    # filers living in the United States, which the model assumes.
    law = calculate(GRID, 2021)
    no_bar = calculate(GRID, 2021, bar=False)
    for v in ["refundable_ctc", "income_tax"]:
        assert np.array_equal(law[v], no_bar[v]), v
    assert not law["refundable_ctc_barred_by_section_911_exclusion"].any()
    # Public Law 114-27, section 807, applies to taxable years beginning
    # after 2014 (refundable_ctc.yaml covers 2014: household simulations
    # need parameters that start later).
    law, no_bar = check(GRID, 2015)
    excludes = law["foreign_earned_income_exclusion"] > 0
    assert (excludes & (no_bar["refundable_ctc"] > 0)).any()
