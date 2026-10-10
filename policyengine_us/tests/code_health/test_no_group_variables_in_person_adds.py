"""Person variables must not add or subtract group variables.

For a variable with no formula for the period, policyengine-core sums its
`adds` list and takes away its `subtracts` list, calling
`simulation.calculate(listed, period, map_to=<the variable's entity>)` for
each listed variable (`Simulation._run_formula`). `Simulation.map_result`
maps a group variable to persons with `population.project`, so every member
of the tax unit, SPM unit, family, marital unit or household receives the
whole group amount. A group total of the person variable then counts it once
per member. The `add()` formula helper raises for the same request, while
these two attributes automatically reach the projection.

A group variable listed by a different group is split evenly over the members
and then summed, and a person variable listed by a group is summed; both keep
totals, so only person-level variables are checked.

A list given as a parameter path is checked at every date in the parameter's
history, because a simulation of an earlier year uses the list in force then.

ALLOWED holds specific reviewed boolean receipt edges, preserving the baseline
interpretation that each member inherits program receipt. A new source or a
subtraction edge still requires review. KNOWN_VIOLATIONS holds open bugs.
Fixing one makes this file fail until its entry is deleted.
"""

from collections import defaultdict
from types import SimpleNamespace

import pytest
from hypothesis import example, given, settings, strategies as st
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
GROUP_ENTITIES = ("tax_unit", "spm_unit", "family", "marital_unit", "household")

# Reviewed positive receipt edges in boolean Person variables. Core casts the
# sum to bool. Exact triples preserve the baseline participation interpretation
# without approving future sources or subtraction edges on the same variable.
ALLOWED = {
    (
        "ks_dcf_csfp_categorically_eligible",
        "adds",
        "snap",
    ): "baseline categorical eligibility from positive SPM-unit SNAP benefits",
    (
        "ks_dcf_csfp_categorically_eligible",
        "adds",
        "receives_snap",
    ): "baseline categorical eligibility from reported SPM-unit SNAP receipt",
    (
        "ks_dcf_csfp_categorically_eligible",
        "adds",
        "fdpir",
    ): "baseline categorical eligibility from positive SPM-unit FDPIR benefits",
    (
        "ma_mbta_enrolled_in_applicable_programs",
        "adds",
        "ma_eaedc",
    ): "baseline enrollment from positive SPM-unit EAEDC benefits",
    (
        "ma_mbta_enrolled_in_applicable_programs",
        "adds",
        "ma_tafdc",
    ): "baseline enrollment from positive SPM-unit TAFDC benefits",
    (
        "ma_mbta_enrolled_in_applicable_programs",
        "adds",
        "snap",
    ): "baseline enrollment from positive SPM-unit SNAP benefits",
    (
        "ma_mbta_enrolled_in_applicable_programs",
        "adds",
        "receives_snap",
    ): "baseline enrollment from reported SPM-unit SNAP receipt",
    (
        "tx_dart_reduced_fare_program_eligible",
        "adds",
        "snap",
    ): "baseline enrollment from positive SPM-unit SNAP benefits",
    (
        "tx_dart_reduced_fare_program_eligible",
        "adds",
        "receives_snap",
    ): "baseline enrollment from reported SPM-unit SNAP receipt",
    (
        "tx_dart_reduced_fare_program_eligible",
        "adds",
        "tanf",
    ): "baseline enrollment from positive SPM-unit TANF benefits",
    (
        "tx_dart_reduced_fare_program_eligible",
        "adds",
        "receives_tanf",
    ): "baseline enrollment from reported SPM-unit TANF receipt",
}

# (person variable, attribute, group variable): each member gets the whole
# group amount. Each was confirmed as a bug on 2026-10-06.
KNOWN_VIOLATIONS = {
    # PolicyEngine/policyengine-us#9888.
    ("mt_misc_deductions", "adds", "casualty_loss_deduction"),
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


def unexpected_group_variables(found, allowed, known) -> dict:
    """Only exact reviewed or known triples exempt a projected group edge."""
    return {
        key: value
        for key, value in found.items()
        if key not in allowed and key not in known
    }


def assert_known_violations_live(found, allowed, known):
    """Recorded bugs must remain live and disjoint from reviewed receipt edges."""
    fixed = sorted(set(known) - found.keys())
    assert not fixed, (
        "No longer projected; delete these from KNOWN_VIOLATIONS:\n"
        + "\n".join(f"{entry}" for entry in fixed)
    )
    overlap = sorted(set(known) & set(allowed))
    assert not overlap, f"Listed as both allowed and a bug: {overlap}"


def assert_allowed_variables_live(found, variables, allowed):
    """Every reviewed edge must remain live, with a boolean Person adds target."""
    stale = sorted(set(allowed) - found.keys())
    assert not stale, "No longer projected; delete these from ALLOWED:\n" + "\n".join(
        f"{entry}" for entry in stale
    )
    not_boolean = sorted(
        {name for name, _, _ in allowed if variables[name].value_type is not bool}
    )
    assert not not_boolean, (
        "ALLOWED covers booleans only, where projection means every member "
        f"inherits the group's value: {not_boolean}"
    )
    not_person = sorted(
        {name for name, _, _ in allowed if not variables[name].entity.is_person}
    )
    assert not not_person, f"ALLOWED covers Person variables only: {not_person}"
    not_adds = sorted(key for key in allowed if key[1] != "adds")
    assert not not_adds, f"ALLOWED covers positive adds edges only: {not_adds}"


def test_person_variables_do_not_add_group_variables():
    new = unexpected_group_variables(FOUND, ALLOWED, KNOWN_VIOLATIONS)
    assert not new, (
        "These person variables list group variables, so core gives every "
        "member the whole group amount. Make the variable group-level, or list "
        "a person-level share. For a reviewed boolean receipt edge that every "
        "member should inherit, add its exact triple to ALLOWED with the reason.\n"
        + "\n".join(
            f"{name}.{attribute} lists {listed} ({entity}; {', '.join(dates)})"
            for (name, attribute, listed), (entity, dates) in sorted(new.items())
        )
    )


def test_known_violations_only_shrink():
    assert_known_violations_live(FOUND, ALLOWED, KNOWN_VIOLATIONS)


def test_allowed_variables_are_booleans_that_still_list_group_variables():
    assert_allowed_variables_live(FOUND, system.variables, ALLOWED)


def test_boolean_exception_does_not_allow_snap_subtraction(monkeypatch):
    target = system.variables["ks_dcf_csfp_categorically_eligible"]
    monkeypatch.setattr(target, "subtracts", ["snap"])
    monkeypatch.setitem(
        globals(),
        "FOUND",
        group_variables_in_person_lists(system.variables, system.parameters),
    )
    # Core attaches each simulation to its system; restore the previous reference.
    monkeypatch.setattr(
        system, "simulation", getattr(system, "simulation", None), raising=False
    )
    simulation = SimulationBuilder().build_from_entities(
        system,
        {
            "people": {
                "recipient": {
                    "ssi": {"2025-05": 0},
                    "receives_ssi": {"2025-05": False},
                    "msp": {"2025-05": 0},
                }
            },
            "households": {
                "household": {
                    "members": ["recipient"],
                    "state_code": {"2025": "KS"},
                }
            },
            "spm_units": {
                "spm_unit": {
                    "members": ["recipient"],
                    "snap": {"2025-05": 100},
                    "receives_snap": {"2025-05": False},
                    "fdpir": {"2025": 0},
                }
            },
        },
    )
    # With reported receipt false and only computed SNAP positive, the sum
    # becomes 0 + False + 100 + False + 0 / 12 + 0 - 100 = 0 (false).
    assert simulation.calculate(target.name, "2025-05").tolist() == [False]
    # The existing positive SNAP edge must not exempt this subtraction.
    with pytest.raises(
        AssertionError,
        match=r"ks_dcf_csfp_categorically_eligible\.subtracts lists snap",
    ):
        test_person_variables_do_not_add_group_variables()


@settings(max_examples=50, deadline=None)
@given(
    group_entity=st.sampled_from(GROUP_ENTITIES),
    edges=st.sets(
        st.tuples(
            st.sampled_from(("flag", "other_flag")),
            st.sampled_from(ATTRIBUTES),
            st.sampled_from(("snap", "fdpir", "tanf")),
        ),
        max_size=12,
    ),
    reviewed_sources=st.sets(st.sampled_from(("snap", "fdpir", "tanf"))),
)
def test_exact_registries_accept_safe_partitions_and_reject_new_edges(
    group_entity, edges, reviewed_sources
):
    reviewed_edge = ("flag", "adds", "snap")
    subtract_snap = ("flag", "subtracts", "snap")
    edges = (edges | {reviewed_edge}) - {subtract_snap}
    found = {key: (group_entity, ["always"]) for key in edges}
    allowed = {
        key: "reviewed positive receipt"
        for key in edges
        if key[1] == "adds" and (key[2] in reviewed_sources or key == reviewed_edge)
    }
    known = edges - allowed.keys()
    variables = {
        name: SimpleNamespace(
            value_type=bool, entity=SimpleNamespace(key="person", is_person=True)
        )
        for name, _, _ in edges
    }
    assert unexpected_group_variables(found, allowed, known) == {}
    assert_known_violations_live(found, allowed, known)
    assert_allowed_variables_live(found, variables, allowed)

    # An allowed name does not approve another source or the opposite attribute.
    for new_edge in (
        ("flag", "adds", "unreviewed_source"),
        ("flag", "subtracts", "unreviewed_source"),
        subtract_snap,
    ):
        changed = {**found, new_edge: (group_entity, ["always"])}
        assert unexpected_group_variables(changed, allowed, known) == {
            new_edge: (group_entity, ["always"])
        }


@settings(max_examples=50, deadline=None)
@given(
    group_entity=st.sampled_from(GROUP_ENTITIES),
    source_index=st.integers(min_value=0, max_value=100),
)
def test_exact_registries_require_live_disjoint_entries(group_entity, source_index):
    first = ("flag", "adds", f"source_{source_index}")
    sibling = ("flag", "adds", f"sibling_{source_index}")
    bug = ("known_bug", "subtracts", f"source_{source_index}")
    found = {key: (group_entity, ["always"]) for key in (first, sibling, bug)}
    allowed = {first: "reviewed receipt", sibling: "another reviewed receipt"}
    known = {bug}
    variables = {
        "flag": SimpleNamespace(
            value_type=bool, entity=SimpleNamespace(key="person", is_person=True)
        )
    }
    assert_known_violations_live(found, allowed, known)
    assert_allowed_variables_live(found, variables, allowed)

    # The variable still lists a group source: only the precise edge went stale.
    without_first = {key: value for key, value in found.items() if key != first}
    with pytest.raises(AssertionError, match="delete these from ALLOWED"):
        assert_allowed_variables_live(without_first, variables, allowed)
    without_bug = {key: value for key, value in found.items() if key != bug}
    with pytest.raises(AssertionError, match="delete these from KNOWN_VIOLATIONS"):
        assert_known_violations_live(without_bug, allowed, known)
    with pytest.raises(AssertionError, match="both allowed and a bug"):
        assert_known_violations_live(found, allowed, known | {first})


@settings(max_examples=50, deadline=None)
@given(
    group_entity=st.sampled_from(GROUP_ENTITIES),
    invalid_schema=st.sampled_from(("integer", "float", "group", "subtracts")),
)
def test_allowed_edges_require_boolean_person_adds(group_entity, invalid_schema):
    attribute = "subtracts" if invalid_schema == "subtracts" else "adds"
    key = ("flag", attribute, "group_amount")
    found = {key: (group_entity, ["always"])}
    target = SimpleNamespace(
        value_type={"integer": int, "float": float}.get(invalid_schema, bool),
        entity=SimpleNamespace(
            key=group_entity if invalid_schema == "group" else "person",
            is_person=invalid_schema != "group",
        ),
    )
    message = {
        "integer": "booleans only",
        "float": "booleans only",
        "group": "Person variables only",
        "subtracts": "positive adds edges only",
    }[invalid_schema]
    with pytest.raises(AssertionError, match=message):
        assert_allowed_variables_live(found, {"flag": target}, {key: "receipt"})


@settings(max_examples=50, deadline=None)
@example(
    group_entity="tax_unit",
    attribute="adds",
    history=[["group_a", "rate"], ["person_amount"]],
)
@given(
    group_entity=st.sampled_from(GROUP_ENTITIES),
    attribute=st.sampled_from(ATTRIBUTES),
    history=st.lists(
        st.lists(
            st.sampled_from(("group_a", "group_b", "person_amount", "rate")),
            max_size=6,
        ),
        min_size=1,
        max_size=5,
    ),
)
def test_parameter_history_preserves_every_group_source(
    group_entity, attribute, history
):
    dates = [f"{2015 + index}-01-01" for index in range(len(history))]
    parameters = ParameterNode(
        "",
        data={"lists": {"sources": {"values": dict(zip(dates, history))}}},
    )
    person = SimpleNamespace(key="person", is_person=True)
    group = SimpleNamespace(key=group_entity, is_person=False)
    target = SimpleNamespace(
        name="from_parameter", entity=person, **{attribute: "lists.sources"}
    )
    variables = {
        "from_parameter": target,
        "person_amount": SimpleNamespace(name="person_amount", entity=person),
        "group_a": SimpleNamespace(name="group_a", entity=group),
        "group_b": SimpleNamespace(name="group_b", entity=group),
        "group_total": SimpleNamespace(
            name="group_total", entity=group, **{attribute: "lists.sources"}
        ),
    }
    expected_dates = {
        name: sorted({date for date, names in zip(dates, history) if name in names})
        for name in {name for names in history for name in names}
    }
    assert listed_names(target, attribute, parameters) == expected_dates
    assert group_variables_in_person_lists(variables, parameters) == {
        ("from_parameter", attribute, name): (group_entity, listed_dates)
        for name, listed_dates in expected_dates.items()
        if name in ("group_a", "group_b")
    }


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


@settings(max_examples=50, deadline=None)
@example(member_count=3, amount=100)
@given(
    member_count=st.integers(min_value=1, max_value=6),
    amount=st.integers(min_value=-1000, max_value=1000),
)
def test_core_projects_group_values_listed_in_person_adds(member_count, amount):
    """Projection repeats a whole group amount; aggregation multiplies it by size."""
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
    members = [f"person_{index}" for index in range(member_count)]
    simulation = SimulationBuilder().build_from_entities(
        template,
        {
            "persons": {member: {} for member in members},
            "households": {
                "h": {
                    "parents": members[:2],
                    "children": members[2:],
                    "household_amount": {"2024": amount},
                }
            },
        },
    )
    assert (
        simulation.calculate("person_adds_household_amount", 2024).tolist()
        == [amount] * member_count
    )
    # The explicit example repeats 100 three times: 3 * 100 = 300.
    assert simulation.calculate("household_sum_of_person_amounts", 2024).tolist() == [
        member_count * amount
    ]
    with pytest.raises(ValueError, match="not yet implemented"):
        simulation.calculate("person_add_helper", 2024)
