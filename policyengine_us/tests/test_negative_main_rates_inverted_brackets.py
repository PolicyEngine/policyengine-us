"""Regression test for issue #9084.

`income_tax_main_rates` walks the bracket schedule with
`amount_between(taxinc, bottom, top)`, where `amount_between` is
`clip(x, bottom, top) - bottom`. NumPy's `clip` with an inverted range
returns the upper bound for every input, so a parameter configuration
whose thresholds are non-monotone for some filing status used to add
`rate * (top - bottom) < 0` to every filer of that status at any
income — a flat negative tax, silently floored downstream of
`income_tax_before_credits` and leaking into state conformity formulas
that reference federal pre-credit liability.

This was not hypothetical: the pre-OBBBA 2026 expiration projections
assigned the single/joint 33%-bracket top ($541,550) to SEPARATE filers,
above their 35%-bracket top ($305,875), producing a flat -$82,486 for
every married-filing-separately filer under TCJA-expiration
counterfactuals.

The fix clamps each bracket top to the running lower bound, so an
inverted bracket contributes zero width and the schedule follows the
monotone envelope of the configured thresholds.
"""

import numpy as np

from policyengine_core.reforms import Reform

from policyengine_us import Simulation

# Recreates the real defect's shape on current law: push the SEPARATE
# bracket-5 top above the enacted bracket-6 top ($384,350 in 2026).
INVERTED_BRACKET_REFORM = Reform.from_dict(
    {
        "gov.irs.income.bracket.thresholds.5.SEPARATE": {
            "2026-01-01.2026-12-31": 541_550
        }
    },
    country_id="us",
)


def separate_filer(employment_income):
    return {
        "people": {
            "adult": {
                "age": 40,
                "employment_income": {"2026": employment_income},
            }
        },
        "tax_units": {"tu": {"members": ["adult"], "filing_status": "SEPARATE"}},
        "households": {"hh": {"members": ["adult"], "state_code": "TX"}},
    }


def test_zero_income_filer_owes_zero_under_inverted_brackets():
    # Sharpest symptom of the bug: a no-income filer of the affected
    # status owed a large negative amount.
    sim = Simulation(reform=INVERTED_BRACKET_REFORM, situation=separate_filer(0))
    main_rates = sim.calculate("income_tax_main_rates", 2026)
    assert main_rates[0] == 0


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
