"""Regression tests for issue #9084.

The bracket-schedule loops compute each bracket's contribution with
`amount_between(taxinc, bottom, top)`, where `amount_between` is
`clip(x, bottom, top) - bottom`. NumPy's `clip` with an inverted range
returns the upper bound for every input, so a parameter configuration
whose thresholds are non-monotone for some filing status used to add
`rate * (top - bottom) < 0` to every filer of that status at any
income — a flat negative tax. The pre-OBBBA 2026 expiration projections
shipped exactly this shape for SEPARATE filers (bracket 5 top $541,550
above bracket 6 top $305,875), worth a flat −$82,486 per
married-filing-separately filer under TCJA-expiration counterfactuals.

Three code sites carry the same loop and all must clamp together:
`income_tax_main_rates`, the AMT regular-tax worksheet
(`regular_tax_before_credits`, taken when the unit has qualified
dividends or long-term gains), and the `additional_tax_bracket` contrib
reform's copies of both. Clamping only the first diverges the AMT
comparator from the corrected main-rates tax and manufactures phantom
AMT for any affected filer with $1 of preferential income.

Note the fixture detail that makes these tests real: situation values
must be period-keyed (`{"2026": ...}`). An undated `filing_status`
lands on the default input period (2024), and a 2026 calculation then
recomputes the status — SINGLE for a lone adult — silently bypassing
the SEPARATE-specific reform under test.
"""

import numpy as np

from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.reforms.additional_tax_bracket.additional_tax_bracket_reform import (
    additional_tax_bracket,
)

# Recreates the shipped defect's shape on current law: push the SEPARATE
# bracket-5 top above the enacted bracket-6 top ($384,350 in 2026).
INVERTED_BRACKET_REFORM = Reform.from_dict(
    {
        "gov.irs.income.bracket.thresholds.5.SEPARATE": {
            "2026-01-01.2026-12-31": 541_550
        }
    },
    country_id="us",
)


def separate_filer(employment_income, qualified_dividends=0):
    person = {
        "age": {"2026": 40},
        "employment_income": {"2026": employment_income},
    }
    if qualified_dividends:
        person["qualified_dividend_income"] = {"2026": qualified_dividends}
    return {
        "people": {"adult": person},
        "tax_units": {
            "tu": {
                "members": ["adult"],
                "filing_status": {"2026": "SEPARATE"},
            }
        },
        "households": {"hh": {"members": ["adult"], "state_code": {"2026": "TX"}}},
    }


def test_fixture_actually_creates_a_separate_filer():
    sim = Simulation(situation=separate_filer(0))
    assert sim.calculate("filing_status", 2026).decode_to_str()[0] == ("SEPARATE")


def test_zero_income_filer_owes_zero_under_inverted_brackets():
    # Sharpest symptom of the bug: a no-income filer of the affected
    # status owed a flat negative amount.
    sim = Simulation(reform=INVERTED_BRACKET_REFORM, situation=separate_filer(0))
    assert sim.calculate("income_tax_main_rates", 2026)[0] == 0


def test_low_income_filer_unaffected_by_inversion_above_their_income():
    # Income far below every modified threshold: the inversion must not
    # change the filer's tax at all.
    baseline = Simulation(situation=separate_filer(50_000))
    reformed = Simulation(
        reform=INVERTED_BRACKET_REFORM, situation=separate_filer(50_000)
    )
    base_val = baseline.calculate("income_tax_main_rates", 2026)[0]
    reform_val = reformed.calculate("income_tax_main_rates", 2026)[0]
    assert base_val > 0
    assert np.isclose(reform_val, base_val)


def test_main_rates_never_negative_across_incomes():
    for income in [0, 10_000, 100_000, 300_000, 500_000, 1_000_000]:
        sim = Simulation(
            reform=INVERTED_BRACKET_REFORM, situation=separate_filer(income)
        )
        assert sim.calculate("income_tax_main_rates", 2026)[0] >= 0


def test_amt_comparator_stays_consistent_with_preferential_income():
    # One dollar of qualified dividends routes the AMT regular-tax
    # comparison through the duplicate worksheet schedule. If that copy
    # is not clamped identically, the corrected main-rates tax minus a
    # still-corrupted comparator manufactures tens of thousands of
    # dollars of phantom AMT.
    sim = Simulation(
        reform=INVERTED_BRACKET_REFORM,
        situation=separate_filer(300_000, qualified_dividends=1),
    )
    amt = sim.calculate("alternative_minimum_tax", 2026)[0]
    main = sim.calculate("income_tax_main_rates", 2026)[0]
    before_credits = sim.calculate("income_tax_before_credits", 2026)[0]
    assert amt == 0
    assert main > 0
    assert abs(before_credits - main) < 2  # only the $1 dividend's tax


def test_mixed_statuses_only_the_separate_row_responds():
    def four_status_situation():
        statuses = {
            "single": "SINGLE",
            "separate": "SEPARATE",
            "hoh": "HEAD_OF_HOUSEHOLD",
            "widow": "SURVIVING_SPOUSE",
        }
        situation = {"people": {}, "tax_units": {}, "households": {}}
        for key, status in statuses.items():
            situation["people"][f"p_{key}"] = {
                "age": {"2026": 40},
                "employment_income": {"2026": 1_000_000},
            }
            situation["tax_units"][f"tu_{key}"] = {
                "members": [f"p_{key}"],
                "filing_status": {"2026": status},
            }
            situation["households"][f"hh_{key}"] = {
                "members": [f"p_{key}"],
                "state_code": {"2026": "TX"},
            }
        return situation

    baseline = Simulation(situation=four_status_situation())
    reformed = Simulation(
        reform=INVERTED_BRACKET_REFORM, situation=four_status_situation()
    )
    statuses = baseline.calculate("filing_status", 2026).decode_to_str()
    base = baseline.calculate("income_tax_main_rates", 2026)
    reform = reformed.calculate("income_tax_main_rates", 2026)
    sep = statuses == "SEPARATE"
    assert sep.sum() == 1
    # Untouched statuses compute identically; the SEPARATE row follows
    # the monotone envelope (a longer 32% band, so less tax, never
    # negative).
    assert np.allclose(reform[~sep], base[~sep])
    assert reform[sep][0] >= 0
    assert reform[sep][0] < base[sep][0]


def test_shipped_additional_tax_bracket_reform_is_clamped():
    # The contrib reform replaces both bracket loops and its parameter
    # tree still carries the expiration projection's inverted SEPARATE
    # thresholds (bracket 5 top 541,550 above bracket 6 top 305,875),
    # so it must clamp too: before the fix a zero-income 2026 MFS filer
    # owed a flat −$82,486 under this shipped reform. The reform's
    # user-supplied extra bracket is filled as in its own yaml tests;
    # brackets 1–6 stay at the shipped (inverted) values.
    fill_extra_bracket = Reform.from_dict(
        {
            "gov.contrib.additional_tax_bracket.bracket.thresholds.7.SEPARATE": {
                "2026-01-01.2026-12-31": 800_000
            },
            "gov.contrib.additional_tax_bracket.bracket.rates.8": {
                "2026-01-01.2026-12-31": 0.42
            },
        },
        country_id="us",
    )
    sim = Simulation(
        reform=(fill_extra_bracket, additional_tax_bracket),
        situation=separate_filer(0),
    )
    main = sim.calculate("income_tax_main_rates", 2026)[0]
    before_credits = sim.calculate("income_tax_before_credits", 2026)[0]
    assert main == 0
    assert before_credits == 0
