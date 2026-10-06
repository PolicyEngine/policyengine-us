"""Person variables must not add or subtract group variables.

For a variable with no formula for the period, policyengine-core sums its
`adds` list and takes away its `subtracts` list, calling
`simulation.calculate(listed, period, map_to=<the variable's entity>)` for
each listed variable (`Simulation._run_formula`). `Simulation.map_result`
maps a group variable to persons with `population.project`, so every member
of the tax unit, SPM unit, family, marital unit or household receives the
whole group amount. A group total of the person variable then counts it once
per member. The `add()` formula helper raises for the same request, so only
these two attributes reach the projection.

A group variable listed by a different group is split evenly over the members
and then summed, and a person variable listed by a group is summed; both keep
totals, so only person-level variables are checked.

A list given as a parameter path is checked at every date in the parameter's
history, because a simulation of an earlier year uses the list in force then.

ALLOWED holds boolean variables where every member should inherit the group's
value. KNOWN_VIOLATIONS holds open bugs. Fixing one makes this file fail until
its entry is deleted, so the list only shrinks.
"""

from collections import defaultdict
from types import SimpleNamespace

import pytest
from policyengine_core.commons.formulas import add
from policyengine_core.country_template import (
    CountryTaxBenefitSystem as TemplateCountrySystem,
)
from policyengine_core.country_template.entities import (
    Household as TemplateHousehold,
    Person as TemplatePerson,
)
from policyengine_core.parameters import Parameter, ParameterNode, get_parameter
from policyengine_core.periods import YEAR
from policyengine_core.simulations import SimulationBuilder
from policyengine_core.variables import Variable

from policyengine_us.system import system


ATTRIBUTES = ("adds", "subtracts")

# Boolean person variables that list SPM-unit program receipt. The sum is cast
# to bool, and each consumer reads it as that person's own program enrollment.
ALLOWED = {
    "ks_dcf_csfp_categorically_eligible": (
        "every member of an SPM unit receiving SNAP or FDPIR participates in it"
    ),
    "ma_mbta_enrolled_in_applicable_programs": (
        "every member of an SPM unit receiving SNAP, TAFDC or EAEDC is enrolled"
    ),
    "tx_dart_reduced_fare_program_eligible": (
        "every member of an SPM unit receiving SNAP or TANF is enrolled"
    ),
}

# (person variable, attribute, group variable): each member gets the whole
# group amount. Each was confirmed as a bug on 2026-10-06.
KNOWN_VIOLATIONS = {
    # PolicyEngine/policyengine-us#9888.
    ("mt_misc_deductions", "adds", "casualty_loss_deduction"),
    # PolicyEngine/policyengine-us#9865.
    ("ms_agi_adjustments", "adds", "health_savings_account_ald"),
    # PolicyEngine/policyengine-us#9856.
    (
        "wv_senior_citizen_disability_deduction_total_modifications",
        "adds",
        "us_govt_interest",
    ),
    (
        "oh_unreimbursed_medical_care_expense_deduction_person",
        "adds",
        "oh_insured_unreimbursed_medical_care_expenses",
    ),
    ("il_aabd_expense_exemption_person", "adds", "state_withheld_income_tax"),
    (
        "ca_riv_general_relief_countable_property_value",
        "adds",
        "ca_riv_general_relief_countable_vehicle_value",
    ),
    (
        "ca_riv_general_relief_countable_property_value",
        "adds",
        "spm_unit_cash_assets",
    ),
    (
        "ca_riv_general_relief_earned_income_deductions",
        "adds",
        "additional_medicare_tax",
    ),
    (
        "ca_riv_general_relief_earned_income_deductions",
        "adds",
        "state_withheld_income_tax",
    ),
    ("la_general_relief_gross_income", "adds", "tanf"),
}


def listed_names(variable, attribute: str, parameters) -> dict[str, list[str]]:
    """Map each name in `variable.<attribute>` to the dates it is listed.

    A list written on the variable applies at every date ("always"). A
    parameter path is read at each value in the parameter's history."""
    listed = getattr(variable, attribute, None)
    if not listed:
        return {}
    if not isinstance(listed, str):
        return {name: ["always"] for name in listed}
    parameter = get_parameter(parameters, listed)
    if not isinstance(parameter, Parameter):
        raise TypeError(
            f"{variable.name}.{attribute} names {listed}, which is not a "
            "parameter holding a list"
        )
    dates = defaultdict(list)
    for value in parameter.values_list:
        for name in value.value or ():
            dates[name].append(value.instant_str)
    return {name: sorted(set(found)) for name, found in dates.items()}


def group_variables_in_person_lists(variables, parameters) -> dict:
    """{(person variable, attribute, group variable): (group entity, dates)}.

    Names that are not variables are parameters, which core adds as values."""
    found = {}
    for name, variable in variables.items():
        if not variable.entity.is_person:
            continue
        for attribute in ATTRIBUTES:
            for listed, dates in listed_names(variable, attribute, parameters).items():
                source = variables.get(listed)
                if source is not None and not source.entity.is_person:
                    found[(name, attribute, listed)] = (source.entity.key, dates)
    return found


FOUND = group_variables_in_person_lists(system.variables, system.parameters)


def test_person_variables_do_not_add_group_variables():
    new = {
        key: value
        for key, value in FOUND.items()
        if key[0] not in ALLOWED and key not in KNOWN_VIOLATIONS
    }
    assert not new, (
        "These person variables list group variables, so core gives every "
        "member the whole group amount. Make the variable group-level, or list "
        "a person-level share. For a boolean that every member should inherit, "
        "add it to ALLOWED with the reason.\n"
        + "\n".join(
            f"{name}.{attribute} lists {listed} ({entity}; {', '.join(dates)})"
            for (name, attribute, listed), (entity, dates) in sorted(new.items())
        )
    )


def test_known_violations_only_shrink():
    fixed = sorted(KNOWN_VIOLATIONS - FOUND.keys())
    assert not fixed, (
        "No longer projected; delete these from KNOWN_VIOLATIONS:\n"
        + "\n".join(f"{entry}" for entry in fixed)
    )
    overlap = sorted(entry for entry in KNOWN_VIOLATIONS if entry[0] in ALLOWED)
    assert not overlap, f"Listed as both allowed and a bug: {overlap}"


def test_allowed_variables_are_booleans_that_still_list_group_variables():
    still_listing = {name for name, _, _ in FOUND}
    stale = sorted(set(ALLOWED) - still_listing)
    assert not stale, f"No longer list a group variable; delete from ALLOWED: {stale}"
    not_boolean = sorted(
        name for name in ALLOWED if system.variables[name].value_type is not bool
    )
    assert not not_boolean, (
        "ALLOWED covers booleans only, where projection means every member "
        f"inherits the group's value: {not_boolean}"
    )


def test_parameter_lists_are_checked_across_their_history():
    parameters = ParameterNode(
        "",
        data={
            "lists": {
                "sources": {
                    "values": {
                        "2015-01-01": ["group_amount", "rate"],
                        "2020-01-01": ["person_amount"],
                    }
                }
            }
        },
    )
    person = SimpleNamespace(key="person", is_person=True)
    group = SimpleNamespace(key="tax_unit", is_person=False)
    variables = {
        "person_amount": SimpleNamespace(name="person_amount", entity=person),
        "group_amount": SimpleNamespace(name="group_amount", entity=group),
        "from_parameter": SimpleNamespace(
            name="from_parameter", entity=person, adds="lists.sources"
        ),
        "from_list": SimpleNamespace(
            name="from_list",
            entity=person,
            adds=["person_amount"],
            subtracts=["group_amount"],
        ),
        "group_total": SimpleNamespace(
            name="group_total", entity=group, adds=["group_amount"]
        ),
    }
    # The 2015 list still counts after 2020 drops it; "rate" is a parameter.
    assert group_variables_in_person_lists(variables, parameters) == {
        ("from_parameter", "adds", "group_amount"): ("tax_unit", ["2015-01-01"]),
        ("from_list", "subtracts", "group_amount"): ("tax_unit", ["always"]),
    }
    # A path to a parameter folder fails rather than checking nothing.
    with pytest.raises(TypeError, match="not a parameter holding a list"):
        listed_names(SimpleNamespace(name="x", adds="lists"), "adds", parameters)


def test_core_projects_group_values_listed_in_person_adds():
    """The premise above, on core's template country: each of a household's
    three members gets the household's whole 100, the household's sum of the
    person variable is 300, and the add() helper refuses the same request."""
    template = TemplateCountrySystem()

    class household_amount(Variable):
        value_type = float
        entity = TemplateHousehold
        definition_period = YEAR
        label = "Household amount"

    class person_adds_household_amount(Variable):
        value_type = float
        entity = TemplatePerson
        definition_period = YEAR
        label = "Person variable adding a household variable"
        adds = ["household_amount"]

    class household_sum_of_person_amounts(Variable):
        value_type = float
        entity = TemplateHousehold
        definition_period = YEAR
        label = "Household sum of the person variable"
        adds = ["person_adds_household_amount"]

    class person_add_helper(Variable):
        value_type = float
        entity = TemplatePerson
        definition_period = YEAR
        label = "Person variable calling add() on a household variable"

        def formula(person, period, parameters):
            return add(person, period, ["household_amount"])

    for variable in (
        household_amount,
        person_adds_household_amount,
        household_sum_of_person_amounts,
        person_add_helper,
    ):
        template.add_variable(variable)
    simulation = SimulationBuilder().build_from_entities(
        template,
        {
            "persons": {"a": {}, "b": {}, "c": {}},
            "households": {
                "h": {
                    "parents": ["a", "b"],
                    "children": ["c"],
                    "household_amount": {"2024": 100},
                }
            },
        },
    )
    assert simulation.calculate("person_adds_household_amount", 2024).tolist() == [
        100,
        100,
        100,
    ]
    assert simulation.calculate("household_sum_of_person_amounts", 2024).tolist() == [
        300
    ]
    with pytest.raises(ValueError, match="not yet implemented"):
        simulation.calculate("person_add_helper", 2024)
