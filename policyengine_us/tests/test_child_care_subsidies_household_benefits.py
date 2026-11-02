"""Invariants of child care subsidies in household benefits.

household_state_benefits counts the child_care_subsidies aggregate, so
gov.hhs.ccdf.child_care_subsidy_programs is the one list of state programs.

1. No state's own subsidy appears beside the aggregate in any year, so no
   subsidy counts twice.
2. A dollar of subsidy adds a dollar to household benefits and to household net
   income, in every state that has a program that year.

The YAML cases pin single families. These read every dated block of the list and
draw from every program and year, which YAML can't express.
"""

from pathlib import Path

import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

PARAMETERS = Path(__file__).parent.parent / "parameters"
STATE_BENEFITS = PARAMETERS / "gov/household/household_state_benefits.yaml"
PROGRAMS = PARAMETERS / "gov/hhs/ccdf/child_care_subsidy_programs.yaml"
TOLERANCE = 0.02


def blocks(path):
    return yaml.load(path.read_text(), Loader=yaml.BaseLoader)["values"]


def programs_in(year):
    dated = [item for item in blocks(PROGRAMS).items() if item[0] <= f"{year}-12-31"]
    return sorted(max(dated)[1])


@pytest.mark.parametrize("instant", sorted(blocks(STATE_BENEFITS)))
def test_each_block_counts_only_the_aggregate(instant):
    members = blocks(STATE_BENEFITS)[instant]
    assert members.count("child_care_subsidies") == 1
    assert set(members) & set(programs_in(instant[:4])) == set()


def net_income_and_benefits(state, year, program, amount):
    members = ["you"]
    situation = {
        "people": {"you": {"age": {year: 40}, "employment_income": {year: 500_000}}},
        "tax_units": {"tax_unit": {"members": members}},
        "spm_units": {"spm_unit": {"members": members, program: {year: amount}}},
        "families": {"family": {"members": members}},
        "marital_units": {"marital_unit": {"members": members}},
        "households": {"household": {"members": members, "state_name": {year: state}}},
    }
    simulation = Simulation(situation=situation)
    return [
        float(simulation.calculate(name, year).sum())
        for name in ("household_net_income", "household_benefits")
    ]


@settings(max_examples=15, deadline=None)
@given(
    year=st.sampled_from([2023, 2024, 2025, 2026]),
    index=st.integers(min_value=0, max_value=50),
    amount=st.integers(min_value=1, max_value=30_000),
)
def test_a_dollar_of_subsidy_adds_a_dollar(year, index, amount):
    programs = programs_in(year)
    program = programs[index % len(programs)]
    state = program[:2].upper()
    without = net_income_and_benefits(state, year, program, 0)
    with_subsidy = net_income_and_benefits(state, year, program, amount)
    for before, after in zip(without, with_subsidy):
        assert after - before == pytest.approx(amount, abs=TOLERANCE)
