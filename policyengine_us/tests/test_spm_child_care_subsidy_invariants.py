"""Invariants for child care subsidies in the Supplemental Poverty Measure.

The Census Bureau's SPM technical documentation (last updated 2026-09-15):

- Page 17 subtracts what parents paid for child care, combined with other work
  expenses and capped at the earnings of the lower earner among the reference
  person and spouse or partner.
- Section 4.3.1 lists the noncash benefits the SPM adds to resources: SNAP,
  school lunch, WIC, energy assistance, internet assistance and housing
  assistance. Child care is not among them.

So a subsidy reaches the SPM once, as a lower expense. With E the pre-subsidy
expense, S the subsidy, W work expenses and C the earnings cap:

    expense(S) = min(W + max(E - S, 0), C)

A unit with a child takes E from its members' pre_subsidy_childcare_expenses,
which an input can set apart from the unit's amount, and a direct
childcare_expenses input replaces max(E - S, 0) altogether. These properties
cover units that leave both to their formulas.

For every SPM unit:

1. The model's expense equals that reference, written from the documentation
   rather than from the formula.
2. A subsidy never raises the expense and lowers it by at most the subsidy:
   0 <= expense(0) - expense(S) <= S. A larger subsidy never raises it either.
3. No double counting. With taxes and every other benefit held fixed, a
   subsidy leaves spm_unit_benefits unchanged and raises spm_unit_net_income
   by exactly expense(0) - expense(S). So this direct effect is never negative
   and never exceeds the subsidy.
4. A subsidy of zero leaves the expense at min(W + max(E, 0), C), the formula
   before this rule, in every state.
5. No program is counted twice. From 2024, no *_child_care_subsidies variable,
   and no program one of them adds, appears in spm_unit_benefits or in a
   reform's copy of that list, and all of them reach child_care_subsidies.
   Before 2024 the expense has no formula, so Colorado's, Washington's and West
   Virginia's subsidies stay resources and count once, as on main. The Tlaib
   reform copies carry only Colorado's in those years, also as on main.
6. Differential. With real programs turned on and off, the expense falls by
   the amount the reference gives for the subsidy the program paid, and the
   SPM and household measures agree on what else changed: the change in SPM
   net income is the change in household net income, less the subsidy the
   household measure counts, plus the fall in the expense.

Intended violation of "a subsidy never lowers SPM resources". Property 3 holds
taxes and other benefits fixed, and it has to. SNAP, TANF and tax credits read
out-of-pocket expenses, so a subsidy can cut them by more than the SPM expense
falls. A unit that stays at the earnings cap shows this most plainly, because
its expense does not move at all, and a benefit cliff can do it below the cap.
Household net income loses the same benefits but also counts the subsidy, so it
can rise while SPM income falls. test_subsidy_at_the_cap_can_lower_spm_income
pins one such case; the fall comes from those programs and not from this rule.

The properties above read spm_unit_pre_subsidy_childcare_expenses as a
pre-subsidy price, which is what it means in a household calculation. Datasets
fill it from the ASEC, which asks parents how much they spent on child care,
and these properties read that amount as what parents paid after any subsidy.
So over a dataset, with E the reported amount, S0 the subsidy baseline policy
pays and S1 the subsidy the simulated policy pays:

    expense(S1) = min(W + max(E - (S1 - S0), 0), C)

7. Baseline policy over a dataset leaves the expense at min(W + E, C), the
   amount Census subtracts, whatever subsidy the model pays.
8. Under any policy over a dataset, the expense equals that reference, with or
   without a child in the unit, and W and C come from the policy simulated. A
   policy that pays the same subsidy and leaves W and C alone leaves the
   expense where baseline policy put it.
9. Differential. Give a dataset the amount the household rule says a unit pays
   at baseline policy. Then the two rules give the same expense under any
   policy. With the same input and real programs, repealing a subsidy moves
   SPM net income by the same amount under both rules, unless the earnings cap
   binds under either.
"""

from functools import cache

import numpy as np
import pytest
import yaml

from policyengine_core.reforms import Reform
from policyengine_us import Simulation
from policyengine_us.system import CountryTaxBenefitSystem
from test_aggregate_list_integrity import (
    BASELINE_SPM_BENEFITS_SOURCE,
    PACKAGE,
    REFORM_AGGREGATE_OVERRIDES,
    benefits_lists_in,
    members_of,
)

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")
example, given, settings = hypothesis.example, hypothesis.given, hypothesis.settings

YEAR = 2026
TOLERANCE = 0.01
# Income variables are float32, which rounds to about $0.03 at the $400,000 the
# fixtures below earn. Every input is a whole dollar, so this still catches a
# $1 error.
INCOME_TOLERANCE = 0.25
PROGRAMS_LIST = "gov/hhs/ccdf/child_care_subsidy_programs.yaml"
STATE_SUBSIDIES = sorted(members_of(PROGRAMS_LIST))
STATES = [name[:2].upper() for name in STATE_SUBSIDIES]


def reference_expense(pre_subsidy, subsidy, work, cap):
    return min(work + max(pre_subsidy - subsidy, 0), cap)


def build_units(units):
    """One SPM unit per entry. The parent's earnings are high enough that no
    means-tested benefit pays, and taxes are an input, so only the child care
    rule can move these units' SPM results."""
    people, tax_units, spm_units, families, households = {}, {}, {}, {}, {}
    marital_units = {}
    for i, unit in enumerate(units):
        parent, child = f"parent_{i}", f"child_{i}"
        people[parent] = {
            "age": {YEAR: 35},
            "employment_income": {YEAR: 400_000},
            "is_tax_unit_head": {YEAR: True},
            "is_household_head": {YEAR: True},
        }
        members = [parent]
        marital_units[f"marital_unit_{i}"] = {"members": [parent]}
        if unit.get("has_child", True):
            people[child] = {"age": {YEAR: 4}, "is_tax_unit_dependent": {YEAR: True}}
            members = [parent, child]
            marital_units[f"child_marital_unit_{i}"] = {"members": [child]}
        state = unit["state"]
        tax_units[f"tax_unit_{i}"] = {"members": members}
        families[f"family_{i}"] = {"members": members}
        spm_units[f"spm_unit_{i}"] = {
            "members": members,
            "spm_unit_pre_subsidy_childcare_expenses": {YEAR: unit["expenses"]},
            "spm_unit_work_expenses": {YEAR: unit["work"]},
            "spm_unit_head_spouse_earned_cap": {YEAR: unit["cap"]},
            f"{state.lower()}_child_care_subsidies": {YEAR: unit["subsidy"]},
            "spm_unit_taxes": {YEAR: 0},
        }
        households[f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: state},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "families": families,
        "marital_units": marital_units,
        "spm_units": spm_units,
        "households": households,
    }


amounts = st.integers(0, 40_000)
unit_strategy = st.fixed_dictionaries(
    {
        "state": st.sampled_from(STATES),
        "expenses": amounts,
        "subsidy": amounts,
        "work": st.integers(0, 6_000),
        "cap": st.integers(0, 60_000),
        "extra_subsidy": st.integers(0, 10_000),
    }
)


def spm_outputs(units):
    simulation = Simulation(situation=build_units(units))
    return {
        variable: np.asarray(simulation.calculate(variable, YEAR), dtype=float)
        for variable in (
            "child_care_subsidies",
            "spm_unit_capped_work_childcare_expenses",
            "spm_unit_benefits",
            "spm_unit_net_income",
        )
    }


@settings(max_examples=25, deadline=None)
@given(st.lists(unit_strategy, min_size=1, max_size=4))
def test_expense_nets_subsidies_exactly_once(units):
    # Each unit runs three times in one simulation: as drawn, with no subsidy
    # and with a larger subsidy.
    without = [{**unit, "subsidy": 0} for unit in units]
    larger = [{**u, "subsidy": u["subsidy"] + u["extra_subsidy"]} for u in units]
    results = spm_outputs(units + without + larger)
    expense = results["spm_unit_capped_work_childcare_expenses"]
    benefits = results["spm_unit_benefits"]
    net_income = results["spm_unit_net_income"]

    n = len(units)
    for i, unit in enumerate(units):
        reference = reference_expense(
            unit["expenses"], unit["subsidy"], unit["work"], unit["cap"]
        )
        no_subsidy = reference_expense(unit["expenses"], 0, unit["work"], unit["cap"])
        # 1. The expense matches the documented definition.
        assert expense[i] == pytest.approx(reference, abs=TOLERANCE)
        assert results["child_care_subsidies"][i] == pytest.approx(
            unit["subsidy"], abs=TOLERANCE
        )
        # 4. Without a subsidy the old formula still holds, in every state.
        assert expense[n + i] == pytest.approx(no_subsidy, abs=TOLERANCE)
        # 2. The fall is at least zero and at most the subsidy, and a larger
        # subsidy never raises the expense.
        fall = expense[n + i] - expense[i]
        assert -TOLERANCE <= fall <= unit["subsidy"] + TOLERANCE
        assert expense[2 * n + i] <= expense[i] + TOLERANCE
        # 3. The subsidy is not a resource, so net income rises by the fall in
        # the expense and by nothing else.
        assert benefits[i] == pytest.approx(benefits[n + i], abs=TOLERANCE)
        gain = net_income[i] - net_income[n + i]
        assert gain == pytest.approx(fall, abs=INCOME_TOLERANCE)


def state_subsidy_adds():
    """{*_child_care_subsidies: the programs it adds}, from the model."""
    from policyengine_us.system import system

    return {name: list(system.variables[name].adds) for name in STATE_SUBSIDIES}


def test_no_subsidy_is_a_spm_resource():
    subsidy_variables = set(STATE_SUBSIDIES) | {"child_care_subsidies"}
    for programs in state_subsidy_adds().values():
        subsidy_variables.update(programs)
    lists = {
        "baseline spm_unit_benefits": benefits_lists_in(BASELINE_SPM_BENEFITS_SOURCE)[
            0
        ][1]
    }
    for path, variable, members in REFORM_AGGREGATE_OVERRIDES:
        if variable == "spm_unit_benefits":
            lists[path] = members
    assert len(lists) >= 5, f"expected the reform copies, found {sorted(lists)}"
    counted_twice = {
        name: sorted(subsidy_variables & set(members))
        for name, members in lists.items()
        if subsidy_variables & set(members)
    }
    assert not counted_twice, (
        "Child care subsidies reach the SPM by lowering "
        f"spm_unit_capped_work_childcare_expenses, not as resources: {counted_twice}"
    )


def test_every_state_subsidy_is_in_the_programs_list():
    variables_dir = PACKAGE / "variables/gov/states"
    defined = {path.stem for path in variables_dir.rglob("*_child_care_subsidies.py")}
    blocks = yaml.load(
        (PACKAGE / "parameters" / PROGRAMS_LIST).read_text(), yaml.BaseLoader
    )["values"]
    # The SPM expense reads the list from 2024, at the start of each year, so a
    # program that starts paying during a year has to be in that year's block.
    assert "2024-01-01" in blocks
    for start, programs in blocks.items():
        if start >= "2024":
            assert defined == set(programs), start
    assert len(defined) == 51


class NoSubsidies(Reform):
    def apply(self):
        for variable in STATE_SUBSIDIES:
            self.neutralize_variable(variable)


@cache
def no_subsidy_system():
    return NoSubsidies(CountryTaxBenefitSystem())


def family(state, earnings, expenses):
    """A working parent and a child aged 3 in full-time care, with real
    programs, taxes and benefits."""
    members = ["parent", "child"]
    return {
        "people": {
            "parent": {
                "age": {YEAR: 30},
                "employment_income": {YEAR: earnings},
                "weekly_hours_worked": {YEAR: 40},
                "weeks_worked": {YEAR: 52},
                "is_tax_unit_head": {YEAR: True},
                "is_household_head": {YEAR: True},
            },
            "child": {
                "age": {YEAR: 3},
                "childcare_hours_per_day": {YEAR: 8},
                "childcare_days_per_week": {YEAR: 5},
                "childcare_attending_days_per_month": {YEAR: 21},
                "is_tax_unit_dependent": {YEAR: True},
            },
        },
        "tax_units": {"tax_unit": {"members": members}},
        "families": {"family": {"members": members}},
        "spm_units": {
            "spm_unit": {
                "members": members,
                "spm_unit_pre_subsidy_childcare_expenses": {YEAR: expenses},
                "meets_ccdf_activity_test": {YEAR: True},
            }
        },
        "households": {"household": {"members": members, "state_code": {YEAR: state}}},
    }


def with_and_without_subsidies(situation):
    on = Simulation(situation=situation)
    off = Simulation(situation=situation, tax_benefit_system=no_subsidy_system())

    def change(variable):
        return float(on.calculate(variable, YEAR).sum()) - float(
            off.calculate(variable, YEAR).sum()
        )

    assert float(off.calculate("child_care_subsidies", YEAR).sum()) == 0
    return on, change


def subsidy_counted_by_household_measure(simulation, state):
    """The subsidy household_state_benefits sums, whether it lists the state's
    variable or the national aggregate."""
    listed = simulation.tax_benefit_system.parameters(
        f"{YEAR}-01-01"
    ).gov.household.household_state_benefits
    state_variable = f"{state.lower()}_child_care_subsidies"
    if "child_care_subsidies" in listed or state_variable in listed:
        return float(simulation.calculate("child_care_subsidies", YEAR).sum())
    return 0.0


@settings(max_examples=12, deadline=None)
@given(
    state=st.sampled_from(STATES),
    earnings=st.integers(5_000, 60_000),
    expenses=st.integers(0, 25_000),
)
# States that left the subsidy out before and states that counted it as a
# resource, at amounts where each program pays.
@example("NY", 30_000, 14_000)
@example("TX", 30_000, 14_000)
@example("AK", 30_000, 14_000)
@example("WA", 30_000, 14_000)
@example("WV", 30_000, 14_000)
@example("CO", 30_000, 14_000)
def test_spm_and_household_measures_agree(state, earnings, expenses):
    on, change = with_and_without_subsidies(family(state, earnings, expenses))
    subsidy = float(on.calculate("child_care_subsidies", YEAR).sum())
    work = float(on.calculate("spm_unit_work_expenses", YEAR).sum())
    cap = float(on.calculate("spm_unit_head_spouse_earned_cap", YEAR).sum())
    fall = -change("spm_unit_capped_work_childcare_expenses")
    assert fall == pytest.approx(
        reference_expense(expenses, 0, work, cap)
        - reference_expense(expenses, subsidy, work, cap),
        abs=TOLERANCE,
    )
    counted = subsidy_counted_by_household_measure(on, state)
    assert change("spm_unit_net_income") == pytest.approx(
        change("household_net_income") - counted + fall, abs=INCOME_TOLERANCE
    )


def test_new_york_subsidy_raises_both_measures_by_the_same_amount():
    # The Manhattan family from the report that prompted this rule.
    situation = family("NY", 30_000, 14_000)
    situation["households"]["household"]["county_fips"] = {YEAR: "36061"}
    del situation["people"]["parent"]["weeks_worked"]
    on, change = with_and_without_subsidies(situation)
    subsidy = float(on.calculate("child_care_subsidies", YEAR).sum())
    assert subsidy > 13_000
    assert change("spm_unit_capped_work_childcare_expenses") == pytest.approx(
        -subsidy, abs=TOLERANCE
    )
    assert change("household_net_income") > 0
    assert change("spm_unit_net_income") == pytest.approx(
        change("household_net_income"), abs=INCOME_TOLERANCE
    )


def test_subsidy_at_the_cap_can_lower_spm_income():
    # Intended: this unit stays at the earnings cap, so the SPM expense does
    # not move, while the fall in out-of-pocket expenses cuts SNAP. See the
    # module docstring.
    on, change = with_and_without_subsidies(family("CA", 8_000, 25_000))
    assert float(on.calculate("child_care_subsidies", YEAR).sum()) > 0
    assert change("spm_unit_capped_work_childcare_expenses") == pytest.approx(
        0, abs=TOLERANCE
    )
    assert change("snap") < 0
    assert change("spm_unit_net_income") == pytest.approx(
        change("spm_unit_benefits") - change("spm_unit_taxes"), abs=INCOME_TOLERANCE
    )
    assert change("spm_unit_net_income") < 0


def with_baseline_arm(simulation):
    """A branch named baseline, wired as a reform simulation wires its own. These
    properties set each arm's subsidy directly, and a real reform builds a whole
    tax-benefit system; the repeal test below and the microsimulation tests run
    that path."""
    simulation.baseline = simulation.get_branch("baseline")
    return simulation


def over_dataset(situation):
    """A simulation that reads its inputs as a dataset's. Core sets this flag
    when it loads a file; a situation lets these properties choose the inputs."""
    simulation = Simulation(situation=situation)
    simulation.is_over_dataset = True
    return simulation


def set_subsidies(simulation, baseline_subsidies, policy_subsidies):
    simulation.baseline.set_input("child_care_subsidies", YEAR, baseline_subsidies)
    simulation.set_input("child_care_subsidies", YEAR, policy_subsidies)


def capped_expense(simulation):
    return np.asarray(
        simulation.calculate("spm_unit_capped_work_childcare_expenses", YEAR),
        dtype=float,
    )


dataset_units = st.lists(
    st.fixed_dictionaries(
        {
            "state": st.sampled_from(STATES),
            "expenses": amounts,
            "subsidy": amounts,
            "policy_subsidy": amounts,
            "work": st.integers(0, 6_000),
            "cap": st.integers(0, 60_000),
            "policy_work": st.integers(0, 6_000),
            "policy_cap": st.integers(0, 60_000),
            "has_child": st.booleans(),
        }
    ),
    min_size=1,
    max_size=4,
)


@settings(max_examples=25, deadline=None)
@given(dataset_units)
def test_baseline_policy_over_a_dataset_keeps_the_reported_amount(units):
    plain = over_dataset(build_units(units))
    simulation = with_baseline_arm(over_dataset(build_units(units)))
    # 7. The subsidy input differs by unit and the expense ignores it. A
    # simulation with no baseline and a baseline arm both hold baseline policy.
    for baseline in (plain, simulation.baseline):
        for unit, expense in zip(units, capped_expense(baseline)):
            assert expense == pytest.approx(
                min(unit["work"] + unit["expenses"], unit["cap"]), abs=TOLERANCE
            )
    # 8. A policy that pays the same subsidy leaves the expense identical, with
    # no rounding error from netting.
    assert (capped_expense(simulation) == capped_expense(simulation.baseline)).all()


@settings(max_examples=25, deadline=None)
@given(dataset_units)
@example(
    # A policy that pays more than the unit reported paying, so the floor binds.
    [
        {
            "state": "NY",
            "expenses": 1_000,
            "subsidy": 0,
            "policy_subsidy": 5_000,
            "work": 100,
            "cap": 60_000,
            "policy_work": 100,
            "policy_cap": 60_000,
            "has_child": True,
        }
    ]
)
@example(
    # A repeal that takes a unit with no child to the earnings cap.
    [
        {
            "state": "TX",
            "expenses": 5_000,
            "subsidy": 8_000,
            "policy_subsidy": 0,
            "work": 100,
            "cap": 6_000,
            "policy_work": 100,
            "policy_cap": 6_000,
            "has_child": False,
        }
    ]
)
@example(
    # A policy that pays the same subsidy but moves work expenses and the cap:
    # 3,500 reads both from the policy, 3,100 would read W and 3,900 would read
    # C from baseline policy.
    [
        {
            "state": "NY",
            "expenses": 3_000,
            "subsidy": 500,
            "policy_subsidy": 500,
            "work": 100,
            "cap": 60_000,
            "policy_work": 900,
            "policy_cap": 3_500,
            "has_child": True,
        }
    ]
)
def test_policy_over_a_dataset_moves_the_expense_by_the_subsidy_change(units):
    # 8. Work expenses and the cap change on the policy's side only, which
    # stores them after the baseline arm branches off.
    simulation = with_baseline_arm(over_dataset(build_units(units)))
    set_subsidies(
        simulation,
        [unit["subsidy"] for unit in units],
        [unit["policy_subsidy"] for unit in units],
    )
    simulation.set_input(
        "spm_unit_work_expenses", YEAR, [unit["policy_work"] for unit in units]
    )
    simulation.set_input(
        "spm_unit_head_spouse_earned_cap",
        YEAR,
        [unit["policy_cap"] for unit in units],
    )
    for unit, expense in zip(units, capped_expense(simulation)):
        assert expense == pytest.approx(
            reference_expense(
                unit["expenses"],
                unit["policy_subsidy"] - unit["subsidy"],
                unit["policy_work"],
                unit["policy_cap"],
            ),
            abs=TOLERANCE,
        )


@settings(max_examples=25, deadline=None)
@given(dataset_units)
def test_dataset_and_household_rules_agree_on_the_expense(units):
    # 9. A subsidy no larger than the price keeps the floor out of the way at
    # baseline policy, so the reported amount is the price less the subsidy.
    baseline_subsidies = [min(u["subsidy"], u["expenses"]) for u in units]
    policy_subsidies = [unit["policy_subsidy"] for unit in units]
    reported = [
        {**unit, "expenses": unit["expenses"] - subsidy}
        for unit, subsidy in zip(units, baseline_subsidies)
    ]
    household = with_baseline_arm(Simulation(situation=build_units(units)))
    dataset = with_baseline_arm(over_dataset(build_units(reported)))
    set_subsidies(household, baseline_subsidies, policy_subsidies)
    set_subsidies(dataset, baseline_subsidies, policy_subsidies)
    assert capped_expense(dataset) == pytest.approx(
        capped_expense(household), abs=TOLERANCE
    )
    assert capped_expense(dataset.baseline) == pytest.approx(
        capped_expense(household.baseline), abs=TOLERANCE
    )


@pytest.mark.parametrize("state, county_fips", [("NY", "36061"), ("TX", None)])
def test_repeal_moves_dataset_and_household_income_by_the_same_amount(
    state, county_fips
):
    # 9. Real programs and a real reform. The dataset reads $14,000 as what
    # parents paid and the household calculation as the price. Neither rule's
    # cap binds and both expenses rise by the subsidy, so SPM income falls by
    # the same amount. The parent's earnings and hours stay raw inputs, which
    # the simulation moves to their pre-response variables: the baseline arm
    # has to read the moved values, or New York's arm sees no hours worked.
    situation = family(state, 30_000, 14_000)
    del situation["people"]["parent"]["weeks_worked"]
    if county_fips:
        situation["households"]["household"]["county_fips"] = {YEAR: county_fips}
    _, household_change = with_and_without_subsidies(situation)
    dataset = Simulation(situation=situation, reform=NoSubsidies)
    dataset.is_over_dataset = True
    dataset.baseline.is_over_dataset = True

    def dataset_change(variable):
        return float(dataset.baseline.calculate(variable, YEAR).sum()) - float(
            dataset.calculate(variable, YEAR).sum()
        )

    subsidy = float(dataset.baseline.calculate("child_care_subsidies", YEAR).sum())
    assert subsidy > 0
    assert float(dataset.calculate("child_care_subsidies", YEAR).sum()) == 0
    assert capped_expense(dataset.baseline).sum() == pytest.approx(
        14_000, abs=TOLERANCE
    )
    assert dataset_change("spm_unit_capped_work_childcare_expenses") == pytest.approx(
        -subsidy, abs=TOLERANCE
    )
    assert household_change("spm_unit_capped_work_childcare_expenses") == pytest.approx(
        -subsidy, abs=TOLERANCE
    )
    assert household_change("spm_unit_net_income") != 0
    assert dataset_change("spm_unit_net_income") == pytest.approx(
        household_change("spm_unit_net_income"), abs=INCOME_TOLERANCE
    )
