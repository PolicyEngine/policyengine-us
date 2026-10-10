"""Hold the abolish-tax reforms' household totals to the baseline totals.

``abolish_federal_income_tax`` and ``abolish_payroll_tax`` redefine
``household_tax_before_refundable_credits`` (and, for the income tax,
``household_refundable_tax_credits``) without the abolished federal component.
Every other baseline component must stay in them: the Idaho permanent building
fund tax, state use taxes, local income and occupational taxes, and each
state's income tax before, not after, its refundable credits.

YAML cannot state these properties, because each compares a reformed total
with the baseline total rather than with a fixed number:

1. Structure, with no simulation: each reformed ``adds`` list is the baseline
   list less the abolished component, however the reforms are ordered or
   repeated, and the baseline lists are left as they were.
2. The same for any list, by Hypothesis draws on ``exclude_from_total``.
3. Values: for 17 households in 15 states, with both reforms applied, each
   reformed total equals the baseline total less the abolished components,
   and net income rises by exactly the abolished taxes less the federal
   refundable credits that go with them.
"""

from collections import Counter
from types import SimpleNamespace

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from policyengine_core.taxbenefitsystems import TaxBenefitSystem

from policyengine_us import Simulation
from policyengine_us.entities import entities
from policyengine_us.model_api import *
from policyengine_us.reforms.federal.abolish_federal_income_tax import (
    abolish_federal_income_tax,
    create_abolish_federal_income_tax_reform,
)
from policyengine_us.reforms.federal.abolish_payroll_tax import (
    abolish_payroll_tax,
    create_abolish_payroll_tax_reform,
)
from policyengine_us.reforms.federal.household_totals import exclude_from_total
from policyengine_us.system import system

TAX = "household_tax_before_refundable_credits"
CREDITS = "household_refundable_tax_credits"
TOTALS = (TAX, CREDITS)
FEDERAL_INCOME_TAX = "income_tax_before_refundable_credits"
FEDERAL_REFUNDABLE_CREDITS = "income_tax_refundable_credits"
PAYROLL_TAX = "employee_payroll_tax"

# reform -> {total: the component the reform excludes from it}
EXCLUSIONS = {
    abolish_federal_income_tax: {
        TAX: FEDERAL_INCOME_TAX,
        CREDITS: FEDERAL_REFUNDABLE_CREDITS,
    },
    abolish_payroll_tax: {TAX: PAYROLL_TAX},
}
REFORM_IDS = {
    abolish_federal_income_tax: "abolish_federal_income_tax",
    abolish_payroll_tax: "abolish_payroll_tax",
}


# Copied at import, before any test applies a reform, so a reform that edited
# the default system's lists in place could not also move what they are
# compared with.
BASELINE_ADDS = {total: tuple(system.variables[total].adds) for total in TOTALS}


def baseline_adds(total):
    return list(BASELINE_ADDS[total])


def reformed_adds(*reforms):
    """Apply reforms to a system that holds only the baseline household totals.

    The reforms read and replace those two variables and nothing else, so this
    needs neither a clone of the full system nor its parameter tree.
    """
    bare = TaxBenefitSystem(entities)
    bare.variables = {total: system.variables[total] for total in TOTALS}
    for reform in reforms:
        reform.apply(bare)
    return {total: list(bare.variables[total].adds) for total in TOTALS}


def expected_adds(*reforms):
    excluded = {total: set() for total in TOTALS}
    for reform in reforms:
        for total, component in EXCLUSIONS[reform].items():
            excluded[total].add(component)
    return {
        total: [c for c in baseline_adds(total) if c not in excluded[total]]
        for total in TOTALS
    }


@pytest.mark.parametrize(
    "total, component",
    [
        (total, component)
        for exclusions in EXCLUSIONS.values()
        for total, component in exclusions.items()
    ],
)
def test_abolished_component_is_in_the_baseline_total(total, component):
    # Excluding an absent component is a silent no-op, so a renamed component
    # must fail here.
    assert baseline_adds(total).count(component) == 1


@pytest.mark.parametrize("reform", EXCLUSIONS, ids=REFORM_IDS.get)
def test_reformed_total_is_baseline_total_less_abolished_component(reform):
    assert reformed_adds(reform) == expected_adds(reform)


@pytest.mark.parametrize(
    "reforms",
    [
        (abolish_federal_income_tax, abolish_payroll_tax),
        (abolish_payroll_tax, abolish_federal_income_tax),
    ],
    ids=["income_tax_then_payroll_tax", "payroll_tax_then_income_tax"],
)
def test_reforms_combine_in_either_order(reforms):
    assert reformed_adds(*reforms) == expected_adds(*reforms)


@pytest.mark.parametrize("reform", EXCLUSIONS, ids=REFORM_IDS.get)
def test_applying_a_reform_again_changes_nothing(reform):
    # CountryTaxBenefitSystem applies a reform more than once.
    assert reformed_adds(reform, reform, reform) == reformed_adds(reform)


@pytest.mark.parametrize(
    "factory, flag, reform",
    [
        (
            create_abolish_federal_income_tax_reform,
            "abolish_federal_income_tax",
            abolish_federal_income_tax,
        ),
        (create_abolish_payroll_tax_reform, "abolish_payroll_tax", abolish_payroll_tax),
    ],
    ids=["abolish_federal_income_tax", "abolish_payroll_tax"],
)
def test_parameter_switches_on_the_same_reform(factory, flag, reform):
    # reforms/reforms.py calls each factory with (parameters, period), so
    # setting the parameter applies the reform without the module-level object.
    def parameters_with(value):
        flat_tax = SimpleNamespace(**{flag: value})
        ubi_center = SimpleNamespace(flat_tax=flat_tax)
        gov = SimpleNamespace(contrib=SimpleNamespace(ubi_center=ubi_center))
        return lambda period: SimpleNamespace(gov=gov)

    assert factory(parameters_with(False), "2025-01-01") is None
    switched_on = factory(parameters_with(True), "2025-01-01")
    assert reformed_adds(switched_on) == expected_adds(reform)


def test_reforms_leave_the_default_system_unchanged():
    variables = {total: system.variables[total] for total in TOTALS}
    reformed_adds(abolish_federal_income_tax, abolish_payroll_tax)
    for total in TOTALS:
        assert system.variables[total] is variables[total]
        assert system.variables[total].adds == baseline_adds(total)


def test_exclude_from_total_changes_nothing_but_adds():
    class total(Variable):
        value_type = float
        entity = Household
        label = "total"
        documentation = "A total."
        unit = USD
        definition_period = YEAR
        defined_for = "eligible"
        adds = ["a", "b"]
        subtracts = ["c"]

    bare = TaxBenefitSystem(entities)
    bare.add_variable(total)
    bare.neutralize_variable("total")
    before = dict(vars(bare.variables["total"]))

    exclude_from_total(bare, "total", "a")
    after = dict(vars(bare.variables["total"]))

    assert before.pop("adds") == ["a", "b"]
    assert after.pop("adds") == ["b"]
    assert after == before
    # Two attributes a new class passed to `update_variable` would reset.
    assert after["defined_for"] == "eligible"
    assert after["is_neutralized"]
    assert bare.data_modified


def test_exclude_from_total_rejects_a_total_computed_by_a_formula():
    class total(Variable):
        value_type = float
        entity = Household
        label = "total"
        definition_period = YEAR

        def formula(household, period, parameters):
            return 0

    without_adds = TaxBenefitSystem(entities)
    without_adds.add_variable(total)
    with pytest.raises(ValueError, match="total must be an `adds` list"):
        exclude_from_total(without_adds, "total", "a")

    # A formula that replaced an `adds` variable inherits the list, but the
    # formula is what is computed.
    with_inherited_adds = system_with_total(["a", "b"])
    with_inherited_adds.update_variable(total)
    assert with_inherited_adds.variables["total"].adds == ["a", "b"]
    with pytest.raises(ValueError, match="total must be an `adds` list"):
        exclude_from_total(with_inherited_adds, "total", "a")


COMPONENT_NAMES = st.sampled_from(["a", "b", "c", "d", "e"])


def system_with_total(adds):
    bare = TaxBenefitSystem(entities)
    bare.add_variable(
        type(
            "total",
            (Variable,),
            dict(
                value_type=float,
                entity=Household,
                label="total",
                definition_period=YEAR,
                adds=adds,
            ),
        )
    )
    return bare


@given(
    adds=st.lists(COMPONENT_NAMES, max_size=8),
    first=COMPONENT_NAMES,
    second=COMPONENT_NAMES,
)
@settings(max_examples=200, deadline=None)
def test_exclude_from_total_properties(adds, first, second):
    original = list(adds)
    bare = system_with_total(adds)

    exclude_from_total(bare, "total", first)
    once = list(bare.variables["total"].adds)
    # Only the excluded component goes, and the rest keep their order.
    assert first not in once
    assert Counter(once) == Counter(c for c in original if c != first)
    assert once == [c for c in original if c in once]
    # The list handed in belongs to the replaced variable and is not edited.
    assert adds == original

    exclude_from_total(bare, "total", first)
    assert bare.variables["total"].adds == once

    exclude_from_total(bare, "total", second)
    other_order = system_with_total(list(original))
    exclude_from_total(other_order, "total", second)
    exclude_from_total(other_order, "total", first)
    assert bare.variables["total"].adds == other_order.variables["total"].adds


YEAR_OF_POPULATION = 2025

# name: (state, household inputs, person inputs, earnings, the tax or credit the
# household is here to exercise). One adult each.
POPULATION = {
    "ID permanent building fund tax": ("ID", {}, {}, 60_000, "id_pbf"),
    "CA use tax": ("CA", {}, {}, 60_000, "ca_use_tax"),
    "IN county tax": (
        "IN",
        {"county_str": "BOONE_COUNTY_IN"},
        {},
        60_000,
        "in_county_tax",
    ),
    "NC use tax": ("NC", {}, {}, 60_000, "nc_use_tax"),
    "OK use tax": ("OK", {}, {}, 60_000, "ok_use_tax"),
    "PA use tax and Philadelphia wage tax": (
        "PA",
        {"county_str": "PHILADELPHIA_COUNTY_PA"},
        {
            "pa_philadelphia_wage_tax_taxable_wages": 60_000,
            "pa_philadelphia_wage_tax_resident": True,
        },
        60_000,
        "pa_philadelphia_wage_tax",
    ),
    "PA use tax and refundable credits": (
        "PA",
        {},
        {},
        12_000,
        "pa_refundable_tax_credits",
    ),
    "IL use tax": ("IL", {}, {}, 60_000, "il_use_tax"),
    "MD county tax": (
        "MD",
        {"county_str": "MONTGOMERY_COUNTY_MD"},
        {},
        60_000,
        "md_local_income_tax_before_refundable_credits",
    ),
    "DE Wilmington earned income tax": (
        "DE",
        {"in_wilmington": True},
        {},
        60_000,
        "de_wilmington_earned_income_tax",
    ),
    "KY Jefferson County occupational tax": (
        "KY",
        {"county_str": "JEFFERSON_COUNTY_KY"},
        {},
        60_000,
        "ky_jefferson_occupational_tax",
    ),
    "MO Kansas City earnings tax": (
        "MO",
        {},
        {"mo_kansas_city_earnings_tax_taxable_earnings": 60_000},
        60_000,
        "mo_kansas_city_earnings_tax",
    ),
    "NY Yonkers surcharge": (
        "NY",
        {"in_yonkers": True},
        {},
        60_000,
        "ny_yonkers_income_tax",
    ),
    "OR Multnomah County tax": (
        "OR",
        {"in_multnomah_county_or": True},
        {},
        200_000,
        "or_multnomah_pfa_tax",
    ),
    "CO Denver occupational privilege tax": (
        "CO",
        {},
        {"co_denver_employee_occupational_privilege_tax_months": 12},
        60_000,
        "co_denver_employee_occupational_privilege_tax",
    ),
    "NY New York City income tax": (
        "NY",
        {"in_nyc": True},
        {},
        60_000,
        "nyc_income_tax_before_refundable_credits",
    ),
    "TX no state or local income tax": ("TX", {}, {}, 60_000, None),
}
EXERCISED = sorted(
    {case[4] for case in POPULATION.values() if case[4]} | {"pa_use_tax"}
)

CALCULATED = [
    TAX,
    CREDITS,
    "household_net_income",
    FEDERAL_INCOME_TAX,
    FEDERAL_REFUNDABLE_CREDITS,
    PAYROLL_TAX,
]

# float32 totals near $200,000 carry about a cent of rounding each.
TOLERANCE = 0.05


def population_situation():
    period = YEAR_OF_POPULATION
    situation = {
        entity: {}
        for entity in (
            "people",
            "households",
            "tax_units",
            "spm_units",
            "families",
            "marital_units",
        )
    }
    for index, (state, household_inputs, person_inputs, earnings, _) in enumerate(
        POPULATION.values()
    ):
        person = f"person_{index}"
        situation["people"][person] = {
            "age": {period: 35},
            "employment_income": {period: earnings},
            **{name: {period: value} for name, value in person_inputs.items()},
        }
        situation["households"][f"household_{index}"] = {
            "members": [person],
            "state_code": {period: state},
            **{name: {period: value} for name, value in household_inputs.items()},
        }
        for entity in ("tax_units", "spm_units", "families", "marital_units"):
            situation[entity][f"{entity}_{index}"] = {"members": [person]}
    return situation


def household_values(simulation, variables):
    return {
        variable: np.asarray(
            simulation.calculate(variable, YEAR_OF_POPULATION, map_to="household"),
            dtype=float,
        )
        for variable in variables
    }


@pytest.fixture(scope="module")
def baseline():
    simulation = Simulation(situation=population_situation())
    return household_values(simulation, CALCULATED + EXERCISED)


@pytest.fixture(scope="module")
def both_reforms():
    # The module-level reform objects leave the abolish parameters false, so
    # each component keeps its baseline value and only the totals can differ.
    # One model build covers both reforms; the structural tests above hold
    # each reform's own lists.
    simulation = Simulation(
        situation=population_situation(),
        reform=(abolish_federal_income_tax, abolish_payroll_tax),
    )
    return household_values(simulation, CALCULATED)


def assert_close(actual, expected):
    np.testing.assert_allclose(actual, expected, rtol=0, atol=TOLERANCE)


def test_each_household_exercises_its_tax(baseline):
    # Otherwise the value check below could pass without testing a component.
    for index, (name, case) in enumerate(POPULATION.items()):
        if case[4]:
            assert baseline[case[4]][index] > 0, name
    pennsylvania = [i for i, case in enumerate(POPULATION.values()) if case[0] == "PA"]
    assert baseline["pa_use_tax"][pennsylvania].min() > 0
    for abolished in (FEDERAL_INCOME_TAX, FEDERAL_REFUNDABLE_CREDITS, PAYROLL_TAX):
        assert baseline[abolished].max() > 0, abolished


def test_abolishing_both_taxes_removes_only_those_taxes(baseline, both_reforms):
    abolished_tax = baseline[FEDERAL_INCOME_TAX] + baseline[PAYROLL_TAX]
    assert_close(both_reforms[TAX], baseline[TAX] - abolished_tax)
    assert_close(
        both_reforms[CREDITS],
        baseline[CREDITS] - baseline[FEDERAL_REFUNDABLE_CREDITS],
    )
    assert_close(
        both_reforms["household_net_income"] - baseline["household_net_income"],
        abolished_tax - baseline[FEDERAL_REFUNDABLE_CREDITS],
    )
