"""Differential coverage of payroll exclusions across vectorized tax units.

Replacing gross wages and pre-tax deductions with the same W-2 box 1 wages
must leave federal EITC and ACTC earnings/credits unchanged. California must
retain taxable payroll HSA amounts, while gross earned income and the AMT
earnings cap must remain independent of payroll deductions. The paired runs
also remove dependents' wages to check that they cannot enter filer earnings.
Additional California pairs retain payroll HSA deductions when substituting
California taxable wages, so YCTC must agree even with business losses.
"""

from copy import deepcopy

import numpy as np

from policyengine_us import Simulation


YEAR = 2026
RANDOM_TAX_UNITS = 24


def _situations():
    rng = np.random.default_rng(20261009)
    people, tax_units, households, marital_units = {}, {}, {}, {}
    for i in range(RANDOM_TAX_UNITS):
        members = [f"head_{i}", f"child_{i}"]
        if i % 2:
            members.insert(1, f"spouse_{i}")
        marital_units[f"filers_{i}"] = {"members": members[:-1]}
        marital_units[f"dependent_{i}"] = {"members": members[-1:]}
        for role, name in zip(
            ["head", "spouse", "child"] if i % 2 else ["head", "child"],
            members,
        ):
            wages = int(rng.integers(10_000, 60_000))
            traditional = int(rng.integers(0, 4_000))
            values = {
                "age": 10 if role == "child" else 35,
                "is_tax_unit_head": role == "head",
                "is_tax_unit_spouse": role == "spouse",
                "is_tax_unit_dependent": role == "child",
                "employment_income": wages,
                "self_employment_income": int(rng.integers(0, 5_000)),
                "traditional_401k_contributions_desired": traditional if i % 3 else 0,
                "traditional_403b_contributions_desired": traditional
                if not i % 3
                else 0,
                "roth_401k_contributions_desired": 1_000,
                "pre_tax_health_insurance_premiums": 500,
                "health_savings_account_payroll_contributions": 1_000,
            }
            people[name] = {key: {YEAR: value} for key, value in values.items()}
        tax_units[f"unit_{i}"] = {
            "members": members,
            "takes_up_eitc": {YEAR: True},
            # Force the existing cap to isolate its gross earnings dependency.
            "amt_kiddie_tax_applies": {YEAR: True},
            "amt_income": {YEAR: 200_000},
        }
        households[f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: "CA" if i % 3 == 0 else "VA"},
        }
    california_wage_pairs = set()
    for i, (wages, traditional, hsa, business_income) in enumerate(
        (
            # Gross wages exceed the YCTC ceiling but taxable wages do not.
            # The business loss leaves zero earned income, invoking Step 8.
            (40_000, 10_000, 0, -30_000),
            (40_000, 10_000, 1_000, -40_000),
            # Also exercise losses leaving positive earnings and SE profits.
            (35_000, 10_000, 1_000, -5_000),
            (25_000, 5_000, 1_000, 2_500),
        ),
        start=RANDOM_TAX_UNITS,
    ):
        members = [f"head_{i}", f"child_{i}"]
        california_wage_pairs.update(members)
        marital_units[f"filers_{i}"] = {"members": members[:1]}
        marital_units[f"dependent_{i}"] = {"members": members[1:]}
        for role, name in zip(("head", "child"), members):
            values = {
                "age": 35 if role == "head" else 4,
                "is_tax_unit_head": role == "head",
                "is_tax_unit_spouse": False,
                "is_tax_unit_dependent": role == "child",
                "employment_income": wages if role == "head" else 0,
                "self_employment_income": business_income if role == "head" else 0,
                "traditional_401k_contributions_desired": traditional
                if role == "head"
                else 0,
                "traditional_403b_contributions_desired": 0,
                "roth_401k_contributions_desired": 0,
                "pre_tax_health_insurance_premiums": 0,
                "health_savings_account_payroll_contributions": hsa
                if role == "head"
                else 0,
            }
            people[name] = {key: {YEAR: value} for key, value in values.items()}
        tax_units[f"unit_{i}"] = {
            "members": members,
            "takes_up_eitc": {YEAR: True},
            "amt_kiddie_tax_applies": {YEAR: True},
            "amt_income": {YEAR: 200_000},
        }
        households[f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: "CA"},
        }
    gross = {
        "people": people,
        "tax_units": tax_units,
        "households": households,
        "marital_units": marital_units,
    }
    taxable = deepcopy(gross)
    without = deepcopy(gross)
    deductions = (
        "traditional_401k_contributions_desired",
        "traditional_403b_contributions_desired",
        "pre_tax_health_insurance_premiums",
        "health_savings_account_payroll_contributions",
    )
    for name, values in people.items():
        wages = values["employment_income"][YEAR]
        excluded = sum(values[key][YEAR] for key in deductions)
        if name in california_wage_pairs:
            # California W-2 box 16 retains payroll HSA contributions.
            # Keeping that deduction in the paired run also preserves the
            # same federal W-2 box 1 wages.
            excluded -= values["health_savings_account_payroll_contributions"][YEAR]
        taxable["people"][name]["employment_income"][YEAR] = wages - excluded
        for key in deductions:
            taxable["people"][name][key][YEAR] = 0
            without["people"][name][key][YEAR] = 0
        if name in california_wage_pairs:
            taxable["people"][name]["health_savings_account_payroll_contributions"][
                YEAR
            ] = values["health_savings_account_payroll_contributions"][YEAR]
        if values["is_tax_unit_dependent"][YEAR]:
            # A child's pay belongs on their own return, not the filer's.
            for key in ("employment_income", "self_employment_income"):
                taxable["people"][name][key][YEAR] = 0
    return gross, taxable, without


def _run(situation):
    simulation = Simulation(situation=situation)
    outputs = (
        "eitc_earned_income",
        "eitc",
        "ctc_phase_in_relevant_earnings",
        "ctc_phase_in",
        "filer_adjusted_earnings",
        "ca_eitc_earned_income",
        "ca_yctc",
        "earned_income",
        "adjusted_earnings",
        "amt_exemption",
    )
    return {name: simulation.calculate(name, YEAR).copy() for name in outputs}


def test_payroll_exclusions_match_equivalent_taxable_compensation():
    gross, taxable, without = _situations()
    with_deductions = _run(gross)
    equivalent_wages = _run(taxable)
    no_deductions = _run(without)

    # Full credit calculations must agree, not just a reimplemented formula.
    for name in (
        "eitc_earned_income",
        "eitc",
        "ctc_phase_in_relevant_earnings",
        "ctc_phase_in",
        "filer_adjusted_earnings",
    ):
        np.testing.assert_allclose(
            with_deductions[name],
            equivalent_wages[name],
            atol=0.01,
            rtol=0,
            err_msg=name,
        )

    # HSA remains California taxable pay, once per nondependent filer.
    california = np.arange(RANDOM_TAX_UNITS) % 3 == 0
    filer_count = 1 + np.arange(RANDOM_TAX_UNITS) % 2
    np.testing.assert_allclose(
        with_deductions["ca_eitc_earned_income"][:RANDOM_TAX_UNITS][california]
        - equivalent_wages["ca_eitc_earned_income"][:RANDOM_TAX_UNITS][california],
        1_000 * filer_count[california],
        atol=0.01,
        rtol=0,
    )

    # Equivalent California compensation must preserve both earned income
    # and YCTC, including its zero-earned-income eligibility branch.
    yctc_pairs = slice(RANDOM_TAX_UNITS, None)
    for name in ("ca_eitc_earned_income", "ca_yctc"):
        np.testing.assert_allclose(
            with_deductions[name][yctc_pairs],
            equivalent_wages[name][yctc_pairs],
            atol=0.01,
            rtol=0,
            err_msg=name,
        )
    np.testing.assert_array_equal(
        with_deductions["ca_eitc_earned_income"][
            RANDOM_TAX_UNITS : RANDOM_TAX_UNITS + 2
        ],
        0,
    )
    assert np.all(with_deductions["ca_yctc"][yctc_pairs] > 0)

    for name in ("earned_income", "adjusted_earnings", "amt_exemption"):
        np.testing.assert_allclose(
            with_deductions[name],
            no_deductions[name],
            atol=0.01,
            rtol=0,
            err_msg=name,
        )
