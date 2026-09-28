"""Uprated inputs supplied only for a year before FIRST_MODELED_YEAR.

Parameters are backdated to FIRST_MODELED_YEAR and no further, so most
uprating indices have no value for an earlier year. policyengine-core used to
divide by that missing value (``TypeError: unsupported operand type(s) for /:
'float' and 'NoneType'``) whenever a later year read the input. Core now holds
the index flat where it has no value, so an early input carries over
unchanged to FIRST_MODELED_YEAR and is uprated from there, exactly as if it
had been supplied for FIRST_MODELED_YEAR.
"""

from collections import defaultdict

import numpy as np
import pytest
from policyengine_core.parameters import get_parameter

from policyengine_us import Simulation
from policyengine_us.system import system
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR

EARLY_YEAR = FIRST_MODELED_YEAR - 2
LATER_YEAR = FIRST_MODELED_YEAR + 5
VALUE = 1_000.0
GROUP_ENTITIES = {
    "tax_unit": "tax_units",
    "spm_unit": "spm_units",
    "family": "families",
    "marital_unit": "marital_units",
    "household": "households",
}


def _index_undefined_before_first_modeled_year(variable) -> bool:
    if variable.uprating is None:
        return False
    index = get_parameter(system.parameters, variable.uprating)
    # The earliest input instant the test supplies.
    return index(f"{EARLY_YEAR}-01-01") is None


AFFECTED = sorted(
    name
    for name, variable in system.variables.items()
    if _index_undefined_before_first_modeled_year(variable)
)


def _periods(variable):
    """The early input period, FIRST_MODELED_YEAR's first period and a later
    period, in the variable's own definition period."""
    if variable.definition_period == "month":
        return (
            f"{FIRST_MODELED_YEAR - 1}-12",
            f"{FIRST_MODELED_YEAR}-01",
            f"{LATER_YEAR}-01",
        )
    return EARLY_YEAR, FIRST_MODELED_YEAR, LATER_YEAR


def _situation(names, defined_for, input_at_first_modeled_year: bool):
    """One person in every group entity, living where the variables are
    defined, with each variable input once."""
    if defined_for is None:
        state = "TX"
    elif defined_for == "in_nyc":
        state = "NY"
    else:
        state = defined_for
    situation = {
        "people": {"p": {"age": {FIRST_MODELED_YEAR: 40}}},
        **{plural: {"g": {"members": ["p"]}} for plural in GROUP_ENTITIES.values()},
    }
    # Geography has formulas (state_code from state_fips, in_nyc from the
    # county), so it is not carried forward: set it for every year read, or
    # the state masks fall back to the default state in LATER_YEAR.
    geography_years = (FIRST_MODELED_YEAR, LATER_YEAR)
    situation["households"]["g"]["state_code"] = {
        year: state for year in geography_years
    }
    if defined_for == "in_nyc":
        situation["households"]["g"]["in_nyc"] = {
            year: True for year in geography_years
        }
    for name in names:
        variable = system.variables[name]
        early, floor, _ = _periods(variable)
        input_period = floor if input_at_first_modeled_year else early
        entity = variable.entity.key
        target = (
            situation["people"]["p"]
            if entity == "person"
            else situation[GROUP_ENTITIES[entity]]["g"]
        )
        target[name] = {input_period: VALUE}
    return situation


def _groups():
    groups = defaultdict(list)
    for name in AFFECTED:
        groups[system.variables[name].defined_for].append(name)
    return sorted(groups.items(), key=lambda item: str(item[0]))


def test_affected_set_is_the_floor_dated_indices():
    # Every dollar input on a floor-dated series (the default AGI-per-capita
    # series and the IRS SOI and CMS per-capita series); CPI-U reaches back
    # to 1913 and is unaffected.
    assert len(AFFECTED) > 300
    assert "tax_exempt_interest_income" in AFFECTED


GROUPS = _groups()


@pytest.mark.parametrize(
    "defined_for,names", GROUPS, ids=[str(defined_for) for defined_for, _ in GROUPS]
)
def test_early_input_behaves_like_first_modeled_year_input(defined_for, names):
    """For every affected variable, an input supplied only for a year before
    FIRST_MODELED_YEAR is carried unchanged to FIRST_MODELED_YEAR, and at a
    later year equals the same input supplied for FIRST_MODELED_YEAR
    (differential)."""
    early_sim = Simulation(situation=_situation(names, defined_for, False))
    floor_sim = Simulation(situation=_situation(names, defined_for, True))
    for name in names:
        _, floor_period, later_period = _periods(system.variables[name])
        at_floor = early_sim.calculate(name, floor_period)
        at_later = early_sim.calculate(name, later_period)
        from_floor = floor_sim.calculate(name, later_period)
        assert at_floor == pytest.approx(VALUE), name
        assert np.isfinite(at_later).all(), name
        # Nonzero: the variable is defined for this household in LATER_YEAR,
        # so the comparison below is not two masked defaults.
        assert (from_floor > 0).all(), name
        assert at_later == pytest.approx(from_floor, rel=1e-6), name


def test_issue_household_with_2013_tax_exempt_interest():
    """The reported household: a 66-year-old in Texas with 2015 wages and
    tax-exempt interest supplied only for 2013."""

    def household(tax_exempt_interest_income):
        return Simulation(
            situation={
                "people": {
                    "p": {
                        "age": {2015: 66},
                        "employment_income": {2015: 30_000},
                        "tax_exempt_interest_income": tax_exempt_interest_income,
                    }
                },
                "households": {"h": {"members": ["p"], "state_code": {2015: "TX"}}},
            }
        )

    early = household({2013: 5_000})
    same_in_2015 = household({2015: 5_000})
    assert early.calculate("tax_exempt_interest_income", 2015) == pytest.approx(5_000)
    for variable in ("income_tax", "household_net_income"):
        assert early.calculate(variable, 2015) == pytest.approx(
            same_in_2015.calculate(variable, 2015)
        ), variable
