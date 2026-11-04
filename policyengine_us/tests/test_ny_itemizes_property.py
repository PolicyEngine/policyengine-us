"""New York's itemizing election never costs more State plus City tax.

``ny_itemizes`` compares, in two branches, only the New York State and New
York City tax the election can move. This checks the choice against the
whole of ``ny_income_tax + nyc_income_tax``: for drawn households, the
model's choice leaves that tax no more than a cent above the other choice's,
calculated in a Simulation of its own with ``ny_itemizes`` set as an input.
YAML cannot draw households or set an input from another simulation's result.
"""

import pytest

pytest.importorskip("hypothesis")

from hypothesis import (  # noqa: E402
    HealthCheck,
    assume,
    given,
    settings,
    strategies as st,
)

from policyengine_us import Simulation  # noqa: E402

YEARS = (2018, 2021, 2024)
TOLERANCE = 0.01


@st.composite
def household(draw):
    return {
        "year": draw(st.sampled_from(YEARS)),
        "nyc": draw(st.booleans()),
        "joint": draw(st.booleans()),
        "wages": draw(st.integers(20_000, 400_000)),
        "tuition": draw(st.sampled_from([0, 2_000, 5_000, 10_000])),
        "property_tax": draw(st.integers(0, 20_000)),
        "child": draw(st.booleans()),
    }


def build_situation(households, year, itemizes=None):
    people, tax_units, marital_units, households_ = {}, {}, {}, {}
    for i, case in enumerate(households):
        head = f"head_{i}"
        members = [head]
        people[head] = {
            "age": {year: 40},
            "employment_income": {year: case["wages"]},
            "qualified_tuition_expenses": {year: case["tuition"]},
            "real_estate_taxes": {year: case["property_tax"]},
        }
        marital_units[f"marital_unit_{i}"] = {"members": [head]}
        if case["joint"]:
            spouse = f"spouse_{i}"
            people[spouse] = {"age": {year: 40}}
            members.append(spouse)
            marital_units[f"marital_unit_{i}"]["members"].append(spouse)
        if case["child"]:
            child = f"child_{i}"
            people[child] = {"age": {year: 5}}
            members.append(child)
            marital_units[f"child_marital_unit_{i}"] = {"members": [child]}
        tax_units[f"tax_unit_{i}"] = {"members": members}
        if itemizes is not None:
            tax_units[f"tax_unit_{i}"]["ny_itemizes"] = {year: bool(itemizes[i])}
        households_[f"household_{i}"] = {
            "members": members,
            "state_code": {year: "NY"},
            "in_nyc": {year: case["nyc"]},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "households": households_,
    }


def state_and_city_tax(simulation, year):
    return simulation.calculate("ny_income_tax", year) + simulation.calculate(
        "nyc_income_tax", year
    )


# Each year builds two Simulations, whose time hardly depends on the number
# of households, so one example draws them all.
@settings(
    max_examples=1,
    deadline=None,
    derandomize=True,
    database=None,
    suppress_health_check=[
        HealthCheck.too_slow,
        HealthCheck.data_too_large,
        HealthCheck.filter_too_much,
    ],
)
@given(households=st.lists(household(), min_size=36, max_size=36))
def test_ny_itemizing_election_costs_no_more_state_and_city_tax(households):
    # Hypothesis first tries the simplest draw, 36 copies of one household.
    assume(len({tuple(case.items()) for case in households}) > 1)
    for year in YEARS:
        cases = [case for case in households if case["year"] == year]
        if not cases:
            continue
        model = Simulation(situation=build_situation(cases, year))
        itemizes = model.calculate("ny_itemizes", year)
        tax = state_and_city_tax(model, year)
        other = Simulation(situation=build_situation(cases, year, ~itemizes))
        other_tax = state_and_city_tax(other, year)
        for case, chosen, mine, theirs in zip(cases, itemizes, tax, other_tax):
            assert mine <= theirs + TOLERANCE, (case, bool(chosen), mine, theirs)
