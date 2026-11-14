"""Check worker-level independence across generated household compositions.

YAML pins the policy amounts and integration examples. Hypothesis also adds,
changes and reorders other household members, and compares each person with
an isolated copy. Every example uses fresh simulation holders and a shared
policy system. The expected amounts preserve the current parameter table.
"""

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

YEARS = [2024, 2025, 2026]
CREDIT = "ne_school_readiness_credit"
ELIGIBLE = "ne_school_readiness_credit_eligible_worker"
LEVEL = "ne_school_readiness_credit_child_care_worker_rating"
CURRENT_AMOUNTS = {1: 2_300, 2: 2_600, 3: 2_900, 4: 3_200, 5: 3_500}

levels = st.one_of(st.none(), st.integers(min_value=-20, max_value=20))
# Each record contains age, worker eligibility and the worker's own level.
members = st.tuples(st.integers(0, 100), st.booleans(), levels)
workers = st.tuples(st.integers(18, 100), st.just(True), levels)


@pytest.fixture(scope="module")
def reference_system():
    return system


def _expected(member):
    _, eligible, level = member
    if not eligible or level is None or level < 1:
        return 0
    return CURRENT_AMOUNTS[min(level, 5)]


def _credits(reference_system, households, year):
    people = {}
    groups = {
        name: {}
        for name in (
            "households",
            "tax_units",
            "families",
            "spm_units",
            "marital_units",
        )
    }
    records = []
    slices = {}
    for name, household in households.items():
        names = []
        start = len(records)
        for index, member in enumerate(household):
            age, eligible, level = member
            person = f"{name}_{index}"
            names.append(person)
            values = {"age": {year: age}, ELIGIBLE: {year: eligible}}
            if level is not None:
                values[LEVEL] = {year: level}
            people[person] = values
            records.append(member)
            groups["marital_units"][person] = {"members": [person]}
        for group in ("households", "tax_units", "families", "spm_units"):
            groups[group][name] = {"members": names}
        groups["households"][name]["state_code"] = {year: "NE"}
        slices[name] = slice(start, len(records))

    simulation = Simulation(
        situation={"people": people, **groups},
        tax_benefit_system=reference_system,
    )
    actual = np.asarray(simulation.calculate(CREDIT, year))
    np.testing.assert_array_equal(actual, [_expected(member) for member in records])
    assert np.isfinite(actual).all()
    assert ((actual >= 0) & (actual <= 3_500)).all()
    eligible = np.array([member[1] for member in records], dtype=bool)
    assert (actual[~eligible] == 0).all()

    # The capped lookup preserves these positive-level amounts.
    positive = np.array(
        [level is not None and level >= 1 for _, _, level in records], dtype=bool
    )
    if positive.any():
        old_levels = np.array(
            [
                min(level, 5)
                for _, _, level in records
                if level is not None and level >= 1
            ]
        )
        table = simulation.tax_benefit_system.parameters(
            year
        ).gov.states.ne.tax.income.credits.school_readiness.amount.refundable
        np.testing.assert_array_equal(
            actual[positive], table[old_levels] * eligible[positive]
        )
    return {name: actual[indices].copy() for name, indices in slices.items()}


@pytest.mark.parametrize("year", YEARS)
@settings(max_examples=12, deadline=None, derandomize=True)
@given(anchor=workers, others=st.lists(members, max_size=6), added=members)
@example(
    anchor=(40, True, None),
    others=[(3, False, None), (42, True, -1), (43, True, 3), (44, True, 5)],
    added=(30, False, 20),
)
@example(
    anchor=(40, True, 3),
    others=[(3, False, None), (42, True, 0), (43, True, 1), (44, True, 20)],
    added=(30, True, 4),
)
def test_credit_depends_only_on_each_workers_own_level(
    reference_system, year, anchor, others, added
):
    drawn = [anchor, *others]
    changed_others = [
        (100 - age, not eligible, -20 if level is not None and level >= 1 else 20)
        for age, eligible, level in others
    ]
    households = {
        "drawn": drawn,
        "reversed": list(reversed(drawn)),
        "extended": [*drawn, added],
        "changed": [anchor, *changed_others],
        **{f"alone_{index}": [member] for index, member in enumerate(drawn)},
    }
    results = _credits(reference_system, households, year)
    np.testing.assert_array_equal(results["drawn"], results["reversed"][::-1])
    np.testing.assert_array_equal(results["drawn"], results["extended"][:-1])
    assert results["drawn"][0] == results["changed"][0]
    for index, amount in enumerate(results["drawn"]):
        assert amount == results[f"alone_{index}"][0]

    # Core returns zero without attempting a lookup when nobody qualifies.
    no_workers = [(age, False, level) for age, _, level in drawn]
    masked = _credits(reference_system, {"no_workers": no_workers}, year)
    np.testing.assert_array_equal(masked["no_workers"], np.zeros(len(drawn)))
