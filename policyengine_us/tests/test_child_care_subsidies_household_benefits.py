"""Invariants of child care subsidies in household benefits.

household_state_benefits counts household_child_care_subsidies, which caps the
child_care_subsidies aggregate, so gov.hhs.ccdf.child_care_subsidy_programs is
the one list of state programs.

1. No state's own subsidy, and not the uncapped aggregate, appears beside
   household_child_care_subsidies in any year, so no subsidy counts twice.
2. With no bill recorded, a dollar of subsidy adds a dollar to household
   benefits and to household net income. Each run samples programs and years.
3. Household benefits count the subsidy up to the family's pre-subsidy bill for
   child care and after-school care. A payment above the bill goes to the
   provider, not the family.

The YAML cases pin single families. These read every dated block of the list and
generate programs, years and amounts, which YAML can't express.
"""

from pathlib import Path

import pytest
import yaml
from hypothesis import example, given, settings
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
    assert members.count("household_child_care_subsidies") == 1
    assert "child_care_subsidies" not in members
    assert set(members) & set(programs_in(instant[:4])) == set()


def test_latest_blocks_list_every_state_program():
    defined = {
        path.stem
        for path in (PARAMETERS.parent / "variables/gov/states").rglob(
            "*_child_care_subsidies.py"
        )
    }
    assert len(defined) == 51
    for start, programs in blocks(PROGRAMS).items():
        if start >= "2025":
            assert set(programs) == defined, start


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


def counted_subsidy(state, year, program, amount, bill, after_school=0):
    members = ["parent", "child"]
    spm_unit = {
        "members": members,
        program: {year: amount},
        "spm_unit_pre_subsidy_childcare_expenses": {year: bill - after_school},
    }
    child = {"age": {year: 3}, "after_school_expenses": {year: after_school}}
    situation = {
        "people": {"parent": {"age": {year: 30}}, "child": child},
        "tax_units": {"tax_unit": {"members": members}},
        "spm_units": {"spm_unit": spm_unit},
        "families": {"family": {"members": members}},
        "marital_units": {"marital_unit": {"members": ["parent"]}},
        "households": {"household": {"members": members, "state_name": {year: state}}},
    }
    simulation = Simulation(situation=situation)
    return float(simulation.calculate("household_child_care_subsidies", year)[0])


@settings(max_examples=15, deadline=None)
# Pin the boundaries the random draws may miss: no bill, a subsidy equal to
# the bill, and a subsidy a dollar above it.
@example(year=2025, index=0, amount=5_000, bill=0, extra=1, after_school_share=0)
@example(year=2025, index=0, amount=5_000, bill=5_000, extra=1, after_school_share=0)
@example(year=2025, index=0, amount=5_001, bill=5_000, extra=1, after_school_share=0)
# After-school care makes up half the bill, and then all of it.
@example(year=2025, index=0, amount=5_000, bill=5_000, extra=1, after_school_share=50)
@example(year=2025, index=0, amount=5_001, bill=5_000, extra=1, after_school_share=100)
@given(
    year=st.sampled_from([2023, 2024, 2025, 2026]),
    index=st.integers(min_value=0, max_value=50),
    amount=st.integers(min_value=0, max_value=30_000),
    bill=st.integers(min_value=0, max_value=30_000),
    extra=st.integers(min_value=1, max_value=30_000),
    after_school_share=st.integers(min_value=0, max_value=100),
)
def test_household_benefits_count_the_subsidy_up_to_the_bill(
    year, index, amount, bill, extra, after_school_share
):
    programs = programs_in(year)
    program = programs[index % len(programs)]
    state = program[:2].upper()
    after_school = bill * after_school_share // 100
    counted = counted_subsidy(state, year, program, amount, bill, after_school)
    assert counted <= amount + TOLERANCE
    if bill > 0:
        assert counted <= bill + TOLERANCE
    if bill == 0 or amount <= bill:
        assert counted == pytest.approx(amount, abs=TOLERANCE)
    if bill > 0:
        bigger = counted_subsidy(
            state, year, program, amount, bill + extra, after_school
        )
        assert bigger >= counted - TOLERANCE
