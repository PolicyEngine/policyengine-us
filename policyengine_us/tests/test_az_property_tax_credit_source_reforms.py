"""Arizona property tax credit income when a reform drops a federal gross
income source.

az_property_tax_credit_agi takes taxable_unemployment_compensation out of
federal AGI, and az_property_tax_credit_nontaxable_income adds the alimony
that federal gross income leaves out, only as far as
gov.irs.gross_income.sources lists the source. These tests drop both sources
and check that each amount is still counted exactly once.

Two Arizona single filers, one per household, aged 40, with no other income
or deductions:

- "uc": $30,000 wages and $5,000 unemployment compensation, $2,000 of it paid
  under another state's law (Form 140PTC line I) and $3,000 under Arizona's
  (excluded by ARS 43-1072(I)).
- "alimony": $20,000 wages and $4,000 alimony under a 2010 divorce, so
  taxable_alimony_income is the full $4,000 at baseline.
"""

import numpy as np
import pytest
from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import Simulation

YEAR = 2025


DROPPED = ["taxable_unemployment_compensation", "taxable_alimony_income"]


class drop_sources(Reform):
    # One reform drops both sources: neither filer has the other's income, so
    # each branch is checked on its own household, and only one reformed
    # system is built.
    def apply(self):
        def modify(parameters):
            node = parameters.gov.irs.gross_income.sources
            start = instant(f"{YEAR}-01-01")
            kept = [s for s in node(start) if s not in DROPPED]
            node.update(start=start, stop=instant(f"{YEAR}-12-31"), value=kept)
            return parameters

        self.modify_parameters(modify)


def _situation() -> dict:
    year = str(YEAR)
    people = {
        "uc": {
            "age": {year: 40},
            "employment_income": {year: 30_000},
            "unemployment_compensation": {year: 5_000},
            "az_other_state_unemployment_compensation": {year: 2_000},
        },
        "alimony": {
            "age": {year: 40},
            "employment_income": {year: 20_000},
            "alimony_income": {year: 4_000},
            "divorce_year": {year: 2010},
        },
    }
    return {
        "people": people,
        "tax_units": {f"{name}_unit": {"members": [name]} for name in people},
        "households": {
            f"{name}_home": {"members": [name], "state_code": {year: "AZ"}}
            for name in people
        },
    }


UC, ALIMONY = 0, 1  # Index of each filer's person, tax unit and household.


@pytest.fixture(scope="module")
def baseline():
    return Simulation(situation=_situation())


@pytest.fixture(scope="module")
def reformed():
    return Simulation(situation=_situation(), reform=drop_sources)


def test_unemployment_left_out_of_gross_income_is_not_subtracted(baseline, reformed):
    # Federal AGI: $30,000 wages + $5,000 unemployment at baseline; the
    # reform leaves the unemployment out, so $30,000.
    assert baseline.calculate("adjusted_gross_income", YEAR)[UC] == 35_000
    assert reformed.calculate("adjusted_gross_income", YEAR)[UC] == 30_000
    # az_property_tax_credit_agi = federal AGI - unemployment that federal AGI
    # holds. Baseline: 35,000 - 5,000 = 30,000. Reform: 30,000 - 0 = 30,000.
    # Subtracting the $5,000 the reform never put in would give 25,000.
    for sim in (baseline, reformed):
        assert sim.calculate("az_property_tax_credit_agi", YEAR)[UC] == 30_000
    # Household income adds back the $2,000 other-state part (line I), once:
    # 30,000 + 2,000 = 32,000 in both.
    for sim in (baseline, reformed):
        assert np.isclose(
            sim.calculate("az_property_tax_credit_household_income", YEAR)[UC],
            32_000,
        )


def test_alimony_left_out_of_gross_income_is_added_in_full(baseline, reformed):
    # Pre-2019 divorce: all $4,000 is taxable_alimony_income at baseline.
    assert baseline.calculate("taxable_alimony_income", YEAR)[ALIMONY] == 4_000
    # Federal AGI: 20,000 + 4,000 = 24,000 at baseline, 20,000 under the reform.
    assert baseline.calculate("adjusted_gross_income", YEAR)[ALIMONY] == 24_000
    assert reformed.calculate("adjusted_gross_income", YEAR)[ALIMONY] == 20_000
    # Nontaxable income = alimony - the part federal gross income holds.
    # Baseline: 4,000 - 4,000 = 0. Reform: none is held, so all 4,000.
    # Reading taxable_alimony_income under the reform would give 0.
    nontaxable = "az_property_tax_credit_nontaxable_income"
    assert baseline.calculate(nontaxable, YEAR)[ALIMONY] == 0
    assert reformed.calculate(nontaxable, YEAR)[ALIMONY] == 4_000
    # Household income counts the alimony once either way:
    # baseline 24,000 (AGI) + 0; reform 20,000 (AGI) + 4,000. Both 24,000.
    for sim in (baseline, reformed):
        assert np.isclose(
            sim.calculate("az_property_tax_credit_household_income", YEAR)[ALIMONY],
            24_000,
        )
