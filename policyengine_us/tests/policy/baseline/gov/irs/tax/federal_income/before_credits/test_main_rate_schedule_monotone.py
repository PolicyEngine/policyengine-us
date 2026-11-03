"""Tax at the main rates never falls when taxable income rises.

YAML cases pin the tax at chosen incomes; this checks the property over a
dense grid of taxable incomes, including one dollar either side of every
bracket threshold, for each filing status and each year from the first
modeled year through the projection years. It covers the pre-2018 schedule
(seven brackets topping out at 39.6%), the switch to the 2018 schedule, and
the uprated thresholds. It calls ``tax_at_main_rates``, the schedule loop that
``income_tax_main_rates`` and ``tax_on_taxable_income_at_main_rates`` use, on
the parameters of the package's shared, already-built system, so it builds no
simulation.
"""

import numpy as np
import pytest

from policyengine_us.system import system
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR
from policyengine_us.variables.gov.irs.tax.federal_income.before_credits.tax_at_main_rates import (
    tax_at_main_rates,
)

FILING_STATUSES = [
    "SINGLE",
    "JOINT",
    "SEPARATE",
    "HEAD_OF_HOUSEHOLD",
    "SURVIVING_SPOUSE",
]
YEARS = range(FIRST_MODELED_YEAR, 2031)


def bracket_node(year):
    return system.parameters(f"{year}-01-01").gov.irs.income.bracket


def rates(bracket):
    return [float(bracket.rates[b]) for b in bracket.rates.__iter__()]


def taxable_income_grid(bracket, status):
    thresholds = [
        float(bracket.thresholds[b][status]) for b in bracket.rates.__iter__()
    ]
    finite = [t for t in thresholds if np.isfinite(t)]
    edges = np.array([t + d for t in finite for d in (-1, 0, 1)])
    grid = np.concatenate([np.arange(0, 1_500_001, 250.0), edges])
    return np.unique(grid[grid >= 0])


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("status", FILING_STATUSES)
def test_tax_never_falls_as_taxable_income_rises(year, status):
    bracket = bracket_node(year)
    income = taxable_income_grid(bracket, status)
    tax = tax_at_main_rates(income, status, bracket)
    assert tax[0] == 0
    step = np.diff(tax)
    # A rise of d dollars of taxable income raises the tax by between zero
    # and the top rate times d.
    top_rate = max(rates(bracket))
    rise = np.diff(income)
    assert np.all(step >= -1e-9), (year, status, income[1:][step < -1e-9])
    assert np.all(step <= top_rate * rise + 1e-6)


def test_pre_2018_schedule_is_the_seven_pre_tcja_rates():
    """2015-2017 use 10% to 39.6%; 2018 starts the 10% to 37% schedule."""
    for year in range(FIRST_MODELED_YEAR, 2018):
        assert rates(bracket_node(year)) == [
            0.10,
            0.15,
            0.25,
            0.28,
            0.33,
            0.35,
            0.396,
        ], year
    assert rates(bracket_node(2018)) == [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("status", FILING_STATUSES)
def test_thresholds_and_rates_strictly_rise(year, status):
    """The clamp in amounts_in_brackets keeps the tax monotone whatever the
    thresholds are, so the property above can't catch a threshold typo. This
    checks the data: each threshold and each rate exceeds the one before."""
    bracket = bracket_node(year)
    keys = list(bracket.rates.__iter__())
    t = [float(bracket.thresholds[b][status]) for b in keys]
    r = rates(bracket)
    assert all(a < b for a, b in zip(t, t[1:])), (year, status, t)
    assert all(a < b for a, b in zip(r, r[1:])), (year, r)
