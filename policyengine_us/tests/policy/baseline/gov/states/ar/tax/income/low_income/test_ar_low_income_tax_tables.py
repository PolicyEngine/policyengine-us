"""Invariants of the Arkansas low-income tax tables, checked at every integer AGI.

`ar_low_income_tax_joint` evaluates these scales with `right=True`. The
published tables charge more tax at higher AGI until a cutoff, above which
filers use the regular tax table (encoded as an infinite amount). The head of
household and surviving spouse files encode the same published column
("Filing Status 3 or 6"), so they must agree. A 2024 data error broke the
first invariant: two brackets shared a threshold, core summed them, and the
table charged $196 at $24,201-$24,300 and then $116 at $24,301-$24,400.
"""

import numpy as np
import pytest
from policyengine_core.parameters import ParameterScale

from policyengine_us.system import system

TABLES = system.parameters.gov.states.ar.tax.income.rates.low_income_tax_tables
SCALES = {
    node.name.removeprefix(TABLES.name + "."): node
    for node in TABLES.get_descendants()
    if isinstance(node, ParameterScale)
}
YEARS = range(2021, 2031)


def _tax_by_integer_agi(scale, year):
    at_instant = scale(f"{year}-01-01")
    top = max(t for t in at_instant.thresholds if np.isfinite(t))
    agi = np.arange(0, int(top) + 2)
    return at_instant.calc(agi, right=True)


def test_tables_cover_every_filing_status_and_dependent_tier():
    assert sorted(SCALES) == [
        "head_of_household.no_or_one_dependent",
        "head_of_household.two_or_more_dependents",
        "joint.no_or_one_dependent",
        "joint.two_or_more_dependents",
        "single",
        "surviving_spouse.no_or_one_dependent",
        "surviving_spouse.two_or_more_dependents",
    ]


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("table", sorted(SCALES))
def test_tax_rises_with_agi_until_the_cutoff(table, year):
    tax = _tax_by_integer_agi(SCALES[table], year)
    finite = np.isfinite(tax)

    assert finite[0] and not finite[-1]
    # Once AGI passes the cutoff it never re-enters the table.
    assert not np.any(finite[1:] & ~finite[:-1])
    assert np.all(np.diff(tax[finite]) >= 0)


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("tier", ["no_or_one_dependent", "two_or_more_dependents"])
def test_head_of_household_and_surviving_spouse_tables_agree(tier, year):
    head_of_household = _tax_by_integer_agi(SCALES[f"head_of_household.{tier}"], year)
    surviving_spouse = _tax_by_integer_agi(SCALES[f"surviving_spouse.{tier}"], year)

    np.testing.assert_array_equal(head_of_household, surviving_spouse)
