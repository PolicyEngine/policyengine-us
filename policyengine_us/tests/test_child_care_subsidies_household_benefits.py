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
4. With a child care bill and no after-school care, the subsidy counted in
   household benefits and the family's remaining expense add up to the bill, in
   every state.
5. Vermont's family balance follows the department's sample invoices: the state
   pays the state rate less the family share, and the family owes tuition less
   that payment. The family owes less than its share when tuition falls below the
   state rate, and its share plus the excess when tuition reaches the state rate.

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


def expense_and_counted_subsidy(state, year, program, amount, bill):
    members = ["parent", "child"]
    spm_unit = {
        "members": members,
        program: {year: amount},
        "spm_unit_pre_subsidy_childcare_expenses": {year: bill},
    }
    situation = {
        "people": {"parent": {"age": {year: 30}}, "child": {"age": {year: 3}}},
        "tax_units": {"tax_unit": {"members": members}},
        "spm_units": {"spm_unit": spm_unit},
        "families": {"family": {"members": members}},
        "marital_units": {"marital_unit": {"members": ["parent"]}},
        "households": {"household": {"members": members, "state_name": {year: state}}},
    }
    simulation = Simulation(situation=situation)
    return [
        float(simulation.calculate(name, year)[0])
        for name in ("childcare_expenses", "household_child_care_subsidies")
    ]


@settings(max_examples=15, deadline=None)
# A subsidy below the bill, equal to it, above it, and none at all.
@example(year=2025, index=0, amount=4_999, bill=5_000)
@example(year=2025, index=0, amount=5_000, bill=5_000)
@example(year=2025, index=0, amount=5_001, bill=5_000)
@example(year=2025, index=0, amount=0, bill=5_000)
@given(
    year=st.sampled_from([2023, 2024, 2025, 2026]),
    index=st.integers(min_value=0, max_value=50),
    amount=st.integers(min_value=0, max_value=30_000),
    bill=st.integers(min_value=1, max_value=30_000),
)
def test_counted_subsidy_and_family_expense_add_up_to_the_bill(
    year, index, amount, bill
):
    programs = programs_in(year)
    program = programs[index % len(programs)]
    state = program[:2].upper()
    expense, counted = expense_and_counted_subsidy(state, year, program, amount, bill)
    assert expense >= 0
    assert expense + counted == pytest.approx(bill, abs=TOLERANCE)


# Full-time preschool at a licensed center, the case in the department's memo of
# January 13, 2026: CDD-Memo-UPK-and-CCFAP-family-tuition, PDF page 6.
VT_STATE_RATE = 439
WEEKS = 52


def vermont_invoice(weekly_tuition, weekly_share):
    year = 2026
    members = ["parent", "child"]
    child = {
        "age": {year: 3},
        "is_tax_unit_dependent": {year: True},
        "vt_ccfap_provider_type": {year: "LICENSED_CENTER"},
        "childcare_days_per_week": {year: 5},
        "childcare_hours_per_day": {year: 7},
    }
    spm_unit = {
        "members": members,
        "vt_ccfap_eligible": {year: True},
        "vt_ccfap_family_share": {year: weekly_share * WEEKS},
        "spm_unit_pre_subsidy_childcare_expenses": {year: weekly_tuition * WEEKS},
    }
    situation = {
        "people": {"parent": {"age": {year: 30}}, "child": child},
        "tax_units": {"tax_unit": {"members": members}},
        "spm_units": {"spm_unit": spm_unit},
        "families": {"family": {"members": members}},
        "marital_units": {"marital_unit": {"members": ["parent"]}},
        "households": {"household": {"members": members, "state_name": {year: "VT"}}},
    }
    simulation = Simulation(situation=situation)
    return [
        float(simulation.calculate(name, year)[0]) / WEEKS
        for name in (
            "child_care_subsidies",
            "childcare_expenses",
            "household_child_care_subsidies",
        )
    ]


@settings(max_examples=15, deadline=None)
# The memo's separate tuition example 1, then tuition equal to the state rate,
# tuition above it, tuition below the state's payment, no share, and a share that
# reaches or passes the state rate.
@example(weekly_tuition=350, weekly_share=300)
@example(weekly_tuition=439, weekly_share=300)
@example(weekly_tuition=500, weekly_share=300)
@example(weekly_tuition=100, weekly_share=300)
@example(weekly_tuition=350, weekly_share=0)
@example(weekly_tuition=350, weekly_share=439)
@example(weekly_tuition=350, weekly_share=500)
@given(
    weekly_tuition=st.integers(min_value=1, max_value=800),
    weekly_share=st.integers(min_value=0, max_value=600),
)
def test_vermont_family_balance_follows_the_department_invoice(
    weekly_tuition, weekly_share
):
    paid, balance, counted = vermont_invoice(weekly_tuition, weekly_share)
    state_payment = max(VT_STATE_RATE - weekly_share, 0)
    assert paid == pytest.approx(state_payment, abs=TOLERANCE)
    assert balance == pytest.approx(
        max(weekly_tuition - state_payment, 0), abs=TOLERANCE
    )
    assert counted == pytest.approx(min(state_payment, weekly_tuition), abs=TOLERANCE)
    if weekly_tuition < VT_STATE_RATE and weekly_share > 0:
        assert balance < weekly_share
    if weekly_tuition >= VT_STATE_RATE and weekly_share <= VT_STATE_RATE:
        excess = weekly_tuition - VT_STATE_RATE
        assert balance == pytest.approx(weekly_share + excess, abs=TOLERANCE)
