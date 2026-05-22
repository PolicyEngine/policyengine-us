"""Regression test for issue #8059.

Calling `refundable_ctc` on an `itemizing` reform branch used to form a
dependency cycle

    refundable_ctc -> ctc_limiting_tax_liability -> (no_salt branch)
      -> income_tax_before_credits -> taxable_income -> tax_unit_itemizes
      -> tax_liability_if_itemizing -> (itemizing branch)
      -> income_tax -> income_tax_before_refundable_credits
      -> income_tax_capped_non_refundable_credits
      -> income_tax_non_refundable_credits -> non_refundable_ctc
      -> refundable_ctc (same variable, new branch) -> ...

which bottomed out as a RecursionError. Surfaced by downstream
consumers (e.g. policyengine.py's household-impact integration tests)
on `policyengine-core >= 3.24`.

The fix in `ctc_limiting_tax_liability.py` propagates the parent's
`tax_unit_itemizes` value to the no_salt child branch so the
`tax_unit_itemizes` formula is never re-entered there.
"""

import numpy as np

from policyengine_us import Simulation


def test_refundable_ctc_on_itemizing_branch_does_not_recurse():
    situation = {
        "people": {
            "adult": {
                "age": 35,
                "employment_income": {"2024": 75_000},
                "real_estate_taxes": 8_000,
            },
            "child": {"age": 8, "is_tax_unit_dependent": True},
        },
        "tax_units": {
            "tu": {
                "members": ["adult", "child"],
                "filing_status": "HEAD_OF_HOUSEHOLD",
            }
        },
        "households": {"hh": {"members": ["adult", "child"], "state_code": "CA"}},
    }
    sim = Simulation(situation=situation)
    itemizing_branch = sim.get_branch("itemizing")
    itemizing_branch.set_input("tax_unit_itemizes", 2024, np.array([True]))

    # Before the fix this raised RecursionError from the
    # refundable_ctc -> ... -> refundable_ctc cycle on the itemizing
    # branch. The value itself is not what we care about; we care
    # that the computation terminates.
    refundable_ctc = itemizing_branch.calculate("refundable_ctc", 2024)
    assert refundable_ctc.shape == (1,)
    assert not np.isnan(refundable_ctc).any()

    # income_tax on the itemizing branch pulls the same chain and
    # must also terminate.
    income_tax = itemizing_branch.calculate("income_tax", 2024)
    assert income_tax.shape == (1,)
    assert not np.isnan(income_tax).any()


def test_income_tax_on_itemizing_branch_with_no_dependents():
    # Matches the minimal single-adult scenario from
    # policyengine.py's TestUSHouseholdImpact tests.
    situation = {
        "people": {
            "adult": {
                "age": 30,
                "employment_income": {"2024": 50_000},
                "is_tax_unit_head": True,
            }
        },
        "tax_units": {"tu": {"members": ["adult"], "filing_status": "SINGLE"}},
        "households": {"hh": {"members": ["adult"], "state_code": "CA"}},
    }
    sim = Simulation(situation=situation)
    itemizing_branch = sim.get_branch("itemizing")
    itemizing_branch.set_input("tax_unit_itemizes", 2024, np.array([True]))

    income_tax = itemizing_branch.calculate("income_tax", 2024)
    assert income_tax.shape == (1,)
    assert not np.isnan(income_tax).any()
