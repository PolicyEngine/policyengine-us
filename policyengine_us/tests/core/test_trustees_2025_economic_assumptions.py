"""Under the 2025 Trustees economic assumptions, a reform that changes only
the payroll cap, or only its owners' draw copy, leaves the benefit wage base
on the assumption's path.

A built system applies its reform set twice, so the assumption's second pass
runs after a policy's first. The assumption extends the wage base from the
wage base's own values, and the owners' draw copy from the draw copy's own
values, so the wage base reads neither the payroll cap nor the draw copy.

Cost: the module builds two systems, the assumption alone and the assumption
plus a cap-only policy, keeping only the values its tests compare, and copies
the default tree once, cached. Replays restore the cached tree's values after
each case.
"""

import math
from contextlib import contextmanager
from functools import lru_cache

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from policyengine_core.parameters import Parameter
from policyengine_core.parameters.operations.get_parameter import get_parameter
from policyengine_core.reforms import Reform

from policyengine_us import CountryTaxBenefitSystem, Simulation
from policyengine_us.reforms.ssa import apply_trustees_2025_economic_assumptions
from policyengine_us.system import system

CAP = "gov.irs.payroll.social_security.cap"
OWNERS_DRAW_CAP = "gov.contrib.ssa.owners_draw.current_law_cap"
WAGE_BASE = "gov.ssa.social_security.wage_base"
END_YEAR = 2100
HOUSEHOLD_YEAR = 2027
HOUSEHOLD_WAGES = 500_000

# The 2025 Trustees cap path from 2036, which the wage base follows; the
# default build's path, which the owners' draw copy held before it followed
# the assumption.
TRUSTEES_2025_CAP = {2036: 261_900, 2050: 430_500, 2100: 2_454_900}
DEFAULT_CAP = {2036: 260_400, 2050: 406_500, 2100: 1_995_300}


def _value(tree, path, year):
    return get_parameter(tree, path)(f"{year}-01-01")


def _entries(tree, path, through=None):
    return [
        (entry.instant_str, entry.value)
        for entry in get_parameter(tree, path).values_list
        if through is None or entry.instant_str <= through
    ]


def _leaves(tree):
    return {
        parameter.name: _entries(tree, parameter.name)
        for parameter in tree.get_descendants()
        if isinstance(parameter, Parameter)
    }


def _value_of(values, path, year):
    """The value in force on 1 January of ``year`` from a list of entries."""
    instant = f"{year}-01-01"
    for start, value in values[path]:
        if start <= instant:
            return value
    raise AssertionError((path, year))


def _assumption():
    def modify_parameters(parameters):
        apply_trustees_2025_economic_assumptions(parameters)
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return reform


def _cap_policy(value):
    def modify_parameters(parameters):
        get_parameter(parameters, CAP).update(start="2027-01-01", value=value)
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return reform


def _covered_earnings(tax_benefit_system):
    situation = {
        "people": {
            "worker": {
                "age": {HOUSEHOLD_YEAR: 40},
                "employment_income": {HOUSEHOLD_YEAR: HOUSEHOLD_WAGES},
            }
        }
    }
    simulation = Simulation(situation=situation, tax_benefit_system=tax_benefit_system)
    covered = simulation.calculate("ss_covered_earnings_this_year", HOUSEHOLD_YEAR)
    return float(covered[0])


@lru_cache(maxsize=None)
def _run(with_cap_policy):
    """Build the assumption, alone or with a policy that removes the payroll
    cap from 2027, and keep only every parameter's values and one worker's
    covered earnings, so the system itself is freed."""
    reform = _assumption()
    if with_cap_policy:
        reform = (reform, _cap_policy(math.inf))
    built = CountryTaxBenefitSystem(reform=reform)
    return _leaves(built.parameters), _covered_earnings(built)


@lru_cache(maxsize=1)
def _applied_once():
    tree = system.parameters.clone()
    apply_trustees_2025_economic_assumptions(tree)
    return tree


@pytest.fixture(scope="module", autouse=True)
def _release_cached_systems():
    """Free what this module builds before later modules run."""
    yield
    for cached in (_run, _paired_leaves, _applied_once):
        cached.cache_clear()


@lru_cache(maxsize=1)
def _paired_leaves():
    """Each parameter of the cached copy with its default-tree twin."""
    copy_leaves = [
        p for p in _applied_once().get_descendants() if isinstance(p, Parameter)
    ]
    default_leaves = [
        p for p in system.parameters.get_descendants() if isinstance(p, Parameter)
    ]
    pairs = list(zip(copy_leaves, default_leaves, strict=True))
    assert all(own.name == default.name for own, default in pairs)
    return pairs


@contextmanager
def _on_default_values():
    """Put every parameter of the cached copy on the default tree's values,
    then give the copy its own values back. Core's ``update`` replaces a
    parameter's value list and never edits the entries in it, so the copy can
    share the default tree's entries meanwhile."""
    pairs = _paired_leaves()
    own = [parameter.values_list for parameter, _ in pairs]

    def put(lists):
        for (parameter, _), values in zip(pairs, lists):
            parameter.values_list = list(values)
            parameter.parent.clear_parent_cache()

    put([default.values_list for _, default in pairs])
    try:
        yield
    finally:
        put(own)


def _replay(reform_set):
    """Apply a reform set twice to a copy of the default tree, as a built
    system does, and return the values the case compares."""
    tree = _applied_once()
    with _on_default_values():
        for apply in reform_set * 2:
            apply(tree)
        return {
            path: _entries(tree, path) for path in (CAP, OWNERS_DRAW_CAP, WAGE_BASE)
        }


def test_wage_base_and_copy_equal_the_cap_under_the_assumption_alone():
    values, _ = _run(False)
    for year in range(2027, END_YEAR + 1):
        assert _value_of(values, WAGE_BASE, year) == _value_of(values, CAP, year)
    for year in range(1994, END_YEAR + 1):
        assert _value_of(values, OWNERS_DRAW_CAP, year) == _value_of(
            values, CAP, year
        ), year


def test_the_copy_moves_to_the_trustees_path_and_the_wage_base_stays():
    """The copy now follows the assumption from 2036 on; the wage base and
    the cap keep the values they had."""
    values, _ = _run(False)
    for year, pin in TRUSTEES_2025_CAP.items():
        assert _value_of(values, CAP, year) == pin
        assert _value_of(values, WAGE_BASE, year) == pin
        assert _value_of(values, OWNERS_DRAW_CAP, year) == pin
        assert _value(system.parameters, OWNERS_DRAW_CAP, year) == DEFAULT_CAP[year]


def test_a_cap_only_policy_moves_no_other_parameter():
    """In a built system, a policy that removes the payroll cap from 2027
    leaves every other parameter equal to the assumption baseline's, entry
    for entry. The replayed passes stand for this build."""
    baseline, _ = _run(False)
    with_policy, _ = _run(True)
    assert with_policy.keys() == baseline.keys()
    differ = sorted(name for name in baseline if with_policy[name] != baseline[name])
    assert differ == [CAP]
    for year in range(2027, END_YEAR + 1):
        assert _value_of(with_policy, CAP, year) == math.inf


def test_covered_earnings_stop_at_the_wage_base_under_a_cap_only_policy():
    _, baseline = _run(False)
    _, with_policy = _run(True)
    assert with_policy == baseline == _value(system.parameters, WAGE_BASE, 2027)
    assert with_policy == 192_300


CAP_POLICIES = {"cap_removed": math.inf, "cap_of_10_million": 10_000_000}


@pytest.mark.parametrize("order", ["assumption_first", "policy_first"])
@pytest.mark.parametrize("policy_cap", CAP_POLICIES.values(), ids=CAP_POLICIES)
def test_wage_base_survives_both_passes_of_a_2027_cap_policy(policy_cap, order):
    def policy(parameters):
        get_parameter(parameters, CAP).update(start="2027-01-01", value=policy_cap)

    reform_set = (apply_trustees_2025_economic_assumptions, policy)
    if order == "policy_first":
        reform_set = reform_set[::-1]
    replayed = _replay(reform_set)
    baseline, _ = _run(False)
    assert replayed[WAGE_BASE] == baseline[WAGE_BASE]
    assert replayed[OWNERS_DRAW_CAP] == baseline[OWNERS_DRAW_CAP]
    for year in range(2027, END_YEAR + 1):
        assert _value_of(replayed, CAP, year) == policy_cap, year


COPY_POLICY_CAP = 10_000_000


@pytest.mark.parametrize("order", ["assumption_first", "policy_first"])
def test_wage_base_survives_both_passes_of_a_2027_owners_draw_copy_policy(order):
    """A policy that sets only the owners' draw copy from 2027 leaves the
    benefit wage base equal to the assumption baseline's, entry for entry,
    after both passes, in either order."""

    def policy(parameters):
        get_parameter(parameters, OWNERS_DRAW_CAP).update(
            start="2027-01-01", value=COPY_POLICY_CAP
        )

    reform_set = (apply_trustees_2025_economic_assumptions, policy)
    if order == "policy_first":
        reform_set = reform_set[::-1]
    replayed = _replay(reform_set)
    baseline, _ = _run(False)
    assert replayed[WAGE_BASE] == baseline[WAGE_BASE]
    for year in range(2027, END_YEAR + 1):
        assert _value_of(replayed, OWNERS_DRAW_CAP, year) == COPY_POLICY_CAP, year


def test_a_policy_after_the_assumption_keeps_the_wage_base_it_sets():
    def policy(parameters):
        for path in (CAP, WAGE_BASE):
            get_parameter(parameters, path).update(start="2027-01-01", value=math.inf)

    replayed = _replay((apply_trustees_2025_economic_assumptions, policy))
    for year in range(2027, END_YEAR + 1):
        assert _value_of(replayed, WAGE_BASE, year) == math.inf, year
    assert [entry for entry in replayed[WAGE_BASE] if entry[0] < "2027"] == _entries(
        system.parameters, WAGE_BASE, "2026-12-31"
    )


PROPERTIES = settings(
    max_examples=25,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)


def _cap_policies():
    """A start year from 2027 to 2100 and a cap from the assumption's cap in
    that year up to no cap. No cap is drawn often."""
    baseline, _ = _run(False)
    return st.integers(2027, END_YEAR).flatmap(
        lambda year: st.tuples(
            st.just(year),
            st.one_of(
                st.just(math.inf),
                st.floats(
                    min_value=_value_of(baseline, CAP, year),
                    allow_nan=False,
                    allow_infinity=True,
                ),
            ),
        )
    )


@PROPERTIES
@given(st.data(), st.booleans())
def test_any_cap_only_policy_leaves_the_wage_base_and_the_copy(data, policy_first):
    start_year, policy_cap = data.draw(_cap_policies())

    def policy(parameters):
        get_parameter(parameters, CAP).update(
            start=f"{start_year}-01-01", value=policy_cap
        )

    reform_set = (apply_trustees_2025_economic_assumptions, policy)
    if policy_first:
        reform_set = reform_set[::-1]
    replayed = _replay(reform_set)
    baseline, _ = _run(False)
    assert replayed[WAGE_BASE] == baseline[WAGE_BASE]
    assert replayed[OWNERS_DRAW_CAP] == baseline[OWNERS_DRAW_CAP]
