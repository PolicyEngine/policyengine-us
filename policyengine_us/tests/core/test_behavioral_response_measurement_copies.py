"""Behavioural responses of clones and branches of a reform simulation.

A reform simulation measures its labour-supply and capital-gains responses
once per period, comparing household net income and marginal tax rates under
the reform and under baseline policy, with the responses neutralized
(``get_behavioral_response_measurements``). These tests cover the copies of
such a simulation, which a single simulation's tests never reach:

- A branch made before anything was calculated used to measure against
  ``branch.get_branch("baseline")``, a new branch under the *reform* policy, so
  its response came out zero. A clone made that early did the same on
  policyengine-core before #587.
- The measurements dictionary lived in the instance ``__dict__``, which core's
  ``clone`` copies by reference, so a clone given other inputs reused its
  source's measurements, and a branch's measurement for a new period landed in
  its parent's dictionary.

Invariants:

1. A clone, at any point, and a branch made before its source measured,
   report the response a new reform simulation with their inputs reports.
2. No two simulations share a measurements dictionary, and a measurement made
   by one never reaches another.
3. A branch made after its source measured starts from a copy of its source's
   measurements. Under d1021 (ruled 2026-10-08), marginal-tax-rate and
   perturbation branches hold responses at the household's measured values.
4. Invalidating a simulation's cached formula output drops its measurements.
"""

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st
from policyengine_core.periods import ETERNITY, YEAR as YEAR_PERIOD
from policyengine_core.periods import period as to_period
from policyengine_core.reforms import Reform
from policyengine_core.variables import Variable

from policyengine_us import Simulation
from policyengine_us.entities import Household, Person
from policyengine_us.spm import BEHAVIORAL_RESPONSE_CACHE_ATTR
from policyengine_us.system import system
from policyengine_us.tools.period_branch import drop_inherited_values
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH,
    _baseline_measurement_branch,
)

YEAR = 2026
FOREVER = f"{YEAR}-01-01.2100-12-31"
RATE_CUT = {"gov.irs.income.bracket.rates.2": {FOREVER: 0.10}}
LSR_REFORM = {
    **RATE_CUT,
    "gov.simulation.labor_supply_responses.elasticities.income": {FOREVER: -0.05},
    "gov.simulation.labor_supply_responses.elasticities.substitution.all": {
        FOREVER: 0.25
    },
}
WAGES = (20_000, 50_000, 100_000)


def household(wages):
    return {
        "people": {"you": {"age": {YEAR: 35}, "employment_income": {YEAR: wages}}},
        "tax_units": {"tu": {"members": ["you"]}},
        "spm_units": {"spm": {"members": ["you"]}},
        "families": {"f": {"members": ["you"]}},
        "marital_units": {"mu": {"members": ["you"]}},
        "households": {"h": {"members": ["you"], "state_name": {YEAR: "CA"}}},
    }


def make_simulation(**kwargs):
    """Reuse read-only policy; each reform gets a private model and inputs."""
    kwargs.setdefault("tax_benefit_system", system)
    return Simulation(**kwargs)


def response(simulation, period=YEAR):
    return np.asarray(
        simulation.calculate("labor_supply_behavioral_response", period),
        dtype=float,
    )


_fresh = {}


def fresh_response(wages, period=YEAR):
    """The response a new reform simulation with these wages reports.

    Values only, so sharing them across tests shares no simulation state.
    """
    key = (wages, period)
    if key not in _fresh:
        _fresh[key] = response(
            make_simulation(situation=household(wages), reform=LSR_REFORM), period
        )
    return _fresh[key]


def set_wages(simulation, wages, period=YEAR):
    """Give a copy other wages, as a marginal-tax-rate branch does its inputs.

    A copy made after its source calculated starts from the source's values,
    and ``set_input`` clears nothing calculated from the old input, so drop
    everything but inputs first.
    """
    drop_inherited_values(simulation)
    simulation.set_input("employment_income_before_lsr", period, np.array([wages]))


@settings(max_examples=3, deadline=None, derandomize=True)
@given(
    kind=st.sampled_from(["clone", "branch"]),
    after_source_measured=st.booleans(),
    source_wages=st.sampled_from(WAGES),
    copy_wages=st.sampled_from(WAGES),
)
# Each of these failed before: zero response, or the source's relative changes.
@example(
    kind="branch", after_source_measured=False, source_wages=50_000, copy_wages=50_000
)
@example(
    kind="clone", after_source_measured=False, source_wages=50_000, copy_wages=50_000
)
@example(
    kind="clone", after_source_measured=True, source_wages=50_000, copy_wages=100_000
)
@example(
    kind="branch", after_source_measured=True, source_wages=50_000, copy_wages=100_000
)
def test_a_copy_reports_the_response_for_its_inputs_and_measurement_state(
    kind, after_source_measured, source_wages, copy_wages
):
    source = make_simulation(situation=household(source_wages), reform=LSR_REFORM)
    if after_source_measured:
        source_response = response(source)
        measured = {
            name: values.copy()
            for name, values in source.__dict__[BEHAVIORAL_RESPONSE_CACHE_ATTR][
                str(YEAR)
            ].items()
        }
    copy = source.clone() if kind == "clone" else source.get_branch("copy")
    if copy_wages != source_wages:
        set_wages(copy, copy_wages)
    copy_response = response(copy)
    if kind == "branch" and after_source_measured:
        # d1021: perturbed wages use the household's measured relative changes.
        # With this reform's uniform elasticities, the response scales with wages.
        np.testing.assert_allclose(
            copy_response, source_response * copy_wages / source_wages, atol=1e-3
        )
        copied_measurements = copy.__dict__[BEHAVIORAL_RESPONSE_CACHE_ATTR][str(YEAR)]
        assert copied_measurements.keys() == measured.keys()
        for name, values in measured.items():
            np.testing.assert_array_equal(copied_measurements[name], values)
    else:
        np.testing.assert_allclose(copy_response, fresh_response(copy_wages), atol=1e-3)
    if after_source_measured:
        np.testing.assert_allclose(
            response(source), fresh_response(source_wages), atol=1e-3
        )


def test_migrated_input_records_are_private_and_explicit_overrides_survive():
    migrated_inputs = {
        "employment_income": ("employment_income_before_lsr", 50_000),
        "self_employment_income": ("self_employment_income_before_lsr", 5_000),
        "sstb_self_employment_income": (
            "sstb_self_employment_income_before_lsr",
            2_000,
        ),
        "weekly_hours_worked": ("weekly_hours_worked_before_lsr", 40),
        "long_term_capital_gains": (
            "long_term_capital_gains_before_response",
            1_000,
        ),
    }
    situation = household(50_000)
    situation["people"]["you"].update(
        {name: {YEAR: value} for name, (_, value) in migrated_inputs.items()}
    )
    source = make_simulation(situation=situation, reform=LSR_REFORM)
    period = to_period(YEAR)
    for original, (migrated, value) in migrated_inputs.items():
        assert (migrated, source.branch_name, period) in source._user_input_keys
        assert (original, source.branch_name, period) not in source._user_input_keys
        # Baseline was copied before migration and must retain its raw inputs.
        assert (
            original,
            source.branch_name,
            period,
        ) in source.baseline._user_input_keys
        np.testing.assert_array_equal(
            source.baseline.calculate(original, YEAR), [value]
        )
    source_input_keys = set(source._user_input_keys)
    baseline_input_keys = set(source.baseline._user_input_keys)

    clone = source.clone()
    override_period = to_period(YEAR + 1)
    override = np.array([123_456.0])
    clone.set_input("employment_income", override_period, override)
    override_key = ("employment_income", clone.branch_name, override_period)
    drop_inherited_values(clone)
    assert override_key in clone._user_input_keys
    np.testing.assert_array_equal(
        clone.get_holder("employment_income").get_array(
            override_period, clone.branch_name
        ),
        override,
    )
    assert source._user_input_keys == source_input_keys
    assert source.baseline._user_input_keys == baseline_input_keys
    assert (
        source.get_holder("employment_income").get_array(
            override_period, source.branch_name
        )
        is None
    )


def test_a_branch_measures_a_new_period_without_touching_its_parent():
    parent = make_simulation(situation=household(50_000), reform=LSR_REFORM)
    response(parent)
    branch = parent.get_branch("next_year")
    set_wages(branch, 100_000, YEAR + 1)
    # The branch's inputs: this year's wages from the household, next year's
    # set exactly (a household's own next-year wages would be uprated).
    fresh = make_simulation(situation=household(50_000), reform=LSR_REFORM)
    fresh.set_input("employment_income_before_lsr", YEAR + 1, np.array([100_000]))
    np.testing.assert_allclose(
        response(branch, YEAR + 1), response(fresh, YEAR + 1), atol=1e-3
    )
    assert str(YEAR + 1) not in parent.__dict__[BEHAVIORAL_RESPONSE_CACHE_ATTR]
    np.testing.assert_allclose(
        response(parent, YEAR + 1), fresh_response(50_000, YEAR + 1), atol=1e-3
    )


def test_copies_own_their_measurements():
    source = make_simulation(situation=household(50_000), reform=LSR_REFORM)
    response(source)
    measurements = source.__dict__[BEHAVIORAL_RESPONSE_CACHE_ATTR]
    assert str(YEAR) in measurements

    clone = source.clone()
    assert BEHAVIORAL_RESPONSE_CACHE_ATTR not in clone.__dict__

    branch = source.get_branch("after")
    copied = branch.__dict__[BEHAVIORAL_RESPONSE_CACHE_ATTR]
    assert copied is not measurements
    assert copied.keys() == measurements.keys()
    # Asking for an existing branch hands it back as it is.
    copied["marker"] = None
    assert source.get_branch("after") is branch
    assert "marker" in branch.__dict__[BEHAVIORAL_RESPONSE_CACHE_ATTR]
    assert "marker" not in measurements


class _no_change(Reform):
    def apply(self):
        pass


def test_invalidating_cached_output_drops_the_measurements():
    simulation = make_simulation(situation=household(50_000), reform=RATE_CUT)
    branch = simulation.get_branch("child")
    for member in (simulation, branch):
        member.__dict__[BEHAVIORAL_RESPONSE_CACHE_ATTR] = {str(YEAR): "stale"}
    # Core's apply_reform (and subsample) purge formula output through
    # _invalidate_all_caches, which reaches every branch.
    simulation.apply_reform(_no_change)
    assert BEHAVIORAL_RESPONSE_CACHE_ATTR not in simulation.__dict__
    assert BEHAVIORAL_RESPONSE_CACHE_ATTR not in branch.__dict__


def test_baseline_measurement_branch_is_baseline_policy_over_the_inputs():
    simulation = make_simulation(situation=household(50_000), reform=RATE_CUT)
    reform_tax = simulation.calculate("income_tax", YEAR)
    expected_tax = simulation.baseline.calculate("income_tax", YEAR)
    assert not np.allclose(reform_tax, expected_tax)

    branch = _baseline_measurement_branch(simulation)
    assert simulation.branches[BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH] is (
        branch
    )
    assert branch.baseline is None
    policy = branch.tax_benefit_system
    assert policy is not simulation.baseline.tax_benefit_system
    assert policy.simulation is branch
    assert policy.parameters(YEAR).gov.irs.income.bracket.rates["2"] == 0.12
    # Nothing calculated under the reform survives, and the inputs do.
    assert not branch.get_holder("income_tax").get_known_periods()
    np.testing.assert_array_equal(
        branch.calculate("employment_income_before_lsr", YEAR), [50_000]
    )
    np.testing.assert_allclose(branch.calculate("income_tax", YEAR), expected_tax)
    np.testing.assert_allclose(simulation.calculate("income_tax", YEAR), reform_tax)
    # The policy is the branch's own: neutralizing in it reaches no one else.
    policy.neutralize_variable("income_tax")
    assert not simulation.baseline.tax_benefit_system.variables[
        "income_tax"
    ].is_neutralized
    simulation.branches.pop(BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH)


def test_baseline_measurement_branch_reads_a_branchs_own_inputs():
    # A reform household's baseline keeps the situation's employment_income as
    # an override from construction, so a branch with other earnings cannot be
    # measured from it.
    simulation = make_simulation(situation=household(50_000), reform=RATE_CUT)
    branch = simulation.get_branch("other_earnings")
    branch.set_input("employment_income_before_lsr", YEAR, np.array([100_000.0]))
    measurement = _baseline_measurement_branch(branch)
    expected = make_simulation(situation=household(100_000)).calculate(
        "household_net_income", YEAR
    )
    np.testing.assert_allclose(
        measurement.calculate("household_net_income", YEAR), expected
    )
    np.testing.assert_allclose(
        simulation.baseline.calculate("household_net_income", YEAR),
        make_simulation(situation=household(50_000)).calculate(
            "household_net_income", YEAR
        ),
    )


def test_baseline_measurement_branch_of_a_traced_simulation():
    simulation = make_simulation(situation=household(50_000), reform=RATE_CUT)
    simulation.trace = True
    branch = _baseline_measurement_branch(simulation)
    assert branch.trace
    assert branch.tracer is simulation.tracer
    # The swapped-in policy gets its own root node, primed for this branch,
    # so its parameter reads are recorded under it, not on the reform's root.
    root = branch.tax_benefit_system.parameters
    assert root is not simulation.tax_benefit_system.parameters
    assert root.trace and root.tracer is simulation.tracer
    assert root.branch_name == BASELINE_BEHAVIORAL_RESPONSE_MEASUREMENT_BRANCH
    assert simulation.tax_benefit_system.parameters.branch_name == "default"


@pytest.mark.parametrize("reform", [None, RATE_CUT])
def test_without_a_baseline_the_baseline_measurement_is_the_simulations_policy(
    reform,
):
    # A simulation built without a reform, or a reform simulation's own
    # baseline, has no baseline: there is no reform, so it is measured against
    # its own policy, and every change is zero.
    built = make_simulation(situation=household(50_000), reform=reform)
    simulation = built if reform is None else built.baseline
    assert simulation.baseline is None
    branch = _baseline_measurement_branch(simulation)
    assert branch.baseline is None
    assert branch.tax_benefit_system is not simulation.tax_benefit_system
    assert branch.tax_benefit_system.parameters(YEAR).gov.irs.income.bracket.rates[
        "2"
    ] == pytest.approx(0.12)
    np.testing.assert_allclose(
        branch.calculate("income_tax", YEAR), simulation.calculate("income_tax", YEAR)
    )


@pytest.mark.parametrize("reform", [None, RATE_CUT])
def test_response_variables_are_zero_without_a_reform(reform):
    # policyengine.py reads these from its baseline simulation, which has no
    # reform; they measure without the labour-supply response's own check.
    built = make_simulation(situation=household(50_000), reform=reform)
    simulation = built if reform is None else built.baseline
    assert response(simulation) == 0
    for variable in (
        "income_elasticity_lsr",
        "substitution_elasticity_lsr",
        "relative_income_change",
        "relative_wage_change",
        "relative_capital_gains_mtr_change",
    ):
        np.testing.assert_array_equal(simulation.calculate(variable, YEAR), [0])


CG_REFORM = {
    **LSR_REFORM,
    "gov.irs.capital_gains.rates.2": {FOREVER: 0.25},
    "gov.simulation.capital_gains_responses.elasticity": {FOREVER: -0.62},
}


def test_capital_gains_marginal_tax_rate_does_not_depend_on_calculation_order():
    # Its branches start from the household's measurements however it is
    # reached: first, or after the household's net income.
    situation = household(60_000)
    situation["people"]["you"]["long_term_capital_gains"] = {YEAR: 200_000}
    first = make_simulation(situation=situation, reform=CG_REFORM)
    rate_first = first.calculate("marginal_tax_rate_on_capital_gains", YEAR)
    after = make_simulation(situation=situation, reform=CG_REFORM)
    after.calculate("household_net_income", YEAR)
    rate_after = after.calculate("marginal_tax_rate_on_capital_gains", YEAR)
    np.testing.assert_allclose(rate_first, rate_after, atol=1e-5)
    np.testing.assert_allclose(
        first.calculate("household_net_income", YEAR),
        after.calculate("household_net_income", YEAR),
    )


@pytest.mark.parametrize("change", ["period", "entity"])
def test_baseline_measurement_drops_incompatible_holders(change):
    # A policy swap must discard holders whose storage or population cannot
    # serve the baseline definition, even when the variable name is the same.
    class is_household_head(Variable):
        definition_period = YEAR_PERIOD if change == "period" else ETERNITY
        entity = Person if change == "period" else Household

    class ChangeHead(Reform):
        def apply(self):
            self.update_variable(is_household_head)

    simulation = make_simulation(
        situation=household(50_000), tax_benefit_system=system, reform=ChangeHead
    )
    # Core creates holders before applying the reform. Recreate this one so
    # its populated storage fits the reform, then becomes unsuitable for
    # baseline policy; an eternal source holder would already fit baseline.
    population = simulation.get_variable_population("is_household_head")
    population._holders.pop("is_household_head", None)
    assert simulation.get_holder("is_household_head")._memory_storage.is_eternal == (
        change == "entity"
    )
    simulation.set_input("is_household_head", YEAR, np.array([True]))
    simulation.calculate("is_household_head", YEAR)
    original_holder = simulation.get_holder("is_household_head")
    branch = _baseline_measurement_branch(simulation)

    for population in branch.populations.values():
        for holder in population._holders.values():
            assert holder.variable.entity.key == population.entity.key
            assert holder._memory_storage.is_eternal == (
                holder.variable.definition_period == ETERNITY
            )
    np.testing.assert_array_equal(
        branch.calculate("is_household_head", YEAR),
        simulation.baseline.calculate("is_household_head", YEAR),
    )
    # Pruning a branch cannot remove the source's holder or change its policy.
    assert simulation.get_holder("is_household_head") is original_holder
    assert (
        original_holder.variable.entity
        is simulation.tax_benefit_system.variables["is_household_head"].entity
    )
    assert original_holder.variable.definition_period == (
        YEAR_PERIOD if change == "period" else ETERNITY
    )


def test_a_fully_calculated_clone_remeasures_changed_wages():
    source = make_simulation(situation=household(50_000), reform=LSR_REFORM)
    original_net_income = source.calculate("household_net_income", YEAR).copy()
    cloned = source.clone()
    set_wages(cloned, 100_000)
    np.testing.assert_allclose(response(cloned), fresh_response(100_000), atol=1e-3)
    np.testing.assert_array_equal(
        source.calculate("household_net_income", YEAR), original_net_income
    )
