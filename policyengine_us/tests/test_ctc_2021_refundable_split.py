"""Vectorized invariants for the 2021 Schedule 8812 refundable/ODC split.

The YAML cases cover complete households. This grid checks the partition across
combinations of child credit, other dependent credit, both reductions and the
refundable cap, using one Core simulation for every year. Inputs stop above the
split so these tests exercise its dependency wiring and the pre-liability
``non_refundable_ctc`` definition without building tax-return branches.

2021 Schedule 8812 lines 12, 14a and 14b, and IRC 24(h)(4), (i)(1)(B),
(i)(4)(D) independently determine the child-only refund and remaining ODC.
Other years retain the existing section 24(d) tax-limit-increase calculation.
"""

from itertools import product

import numpy as np
import pytest
from policyengine_core.simulations import SimulationBuilder

from policyengine_us.system import system


OTHER_YEARS = (2018, 2020, 2022, 2025, 2026)
# First-reduction fractions include both ends of the ARPA-increase cap. The
# ordinary reduction extends beyond all child credit and then all ODC.
GRID = np.asarray(
    list(
        product(
            (0, 1),  # children under 6
            (0, 1),  # children 6 through 17
            (0, 1, 2),  # other dependents
            (0, 0.5, 1),  # share of the ARPA increase removed
            (0, 50, 500, 2_000, 4_000, 8_000, 20_000),
        )
    )
)


@pytest.fixture(scope="module")
def split_grid():
    # A second copy gives each case a smaller refundable maximum. This guards
    # the existing cap contract without making a second, mutable reform tree.
    cases = np.concatenate((GRID, GRID))
    young, older, other_dependents, first_share, ordinary = cases.T
    children = young + older
    count = len(cases)
    baseline = np.arange(count) < len(GRID)
    simulation = SimulationBuilder().build_default_simulation(system, count)
    phase_in = np.resize([0, 300, 1_500, 10_000], count)
    liability = np.resize([0, 250, 2_000, 20_000], count)
    barred = np.resize([False, False, False, True, False], count)
    references = {}

    for year in (2021, *OTHER_YEARS):
        p = system.parameters(f"{year}-01-01").gov.irs.credits.ctc
        base_per_child = p.amount.base.calc(np.array([5]))[0]
        base_children = children * base_per_child
        other_credit = other_dependents * p.amount.adult_dependent
        if year == 2021:
            child_credit = young * 3_600 + older * 3_000
            addition = child_credit - base_children
            first = addition * first_share
            maximum = np.where(baseline, child_credit, child_credit / 2)
        else:
            child_credit = base_children
            addition = np.zeros(count)
            first = np.zeros(count)
            maximum = children * min(base_per_child, p.refundable.individual_max)

        inputs = {
            "filer_meets_ctc_identification_requirements": np.ones(count, dtype=bool),
            "ctc_maximum": base_children + other_credit,
            "ctc_arpa_max_addition": addition,
            "ctc_arpa_phase_out": first,
            "ctc_phase_out": ordinary,
            "ctc_refundable_maximum": maximum,
            "ctc_phase_in": phase_in,
            "ctc_limiting_tax_liability": liability,
            "refundable_ctc_barred_by_section_911_exclusion": barred,
        }
        for name, values in inputs.items():
            simulation.set_input(name, year, values)
        references[year] = {
            "child": child_credit,
            "other": other_credit,
            "first": first,
            "ordinary": ordinary,
            "maximum": maximum,
            "total": np.maximum(child_credit + other_credit - first - ordinary, 0),
        }

    return simulation, references, baseline, phase_in, liability, barred


def test_2021_schedule_8812_partition_before_tax_limit(split_grid):
    simulation, references, baseline, _, liability, _ = split_grid
    r = references[2021]
    total = simulation.calculate("ctc", 2021)
    refundable = simulation.calculate("refundable_ctc", 2021)
    non_refundable = simulation.calculate("non_refundable_ctc", 2021)
    child_after_reductions = np.maximum(r["child"] - r["first"] - r["ordinary"], 0)

    # Schedule 8812 line 14a excludes ODC and applies both reductions. Identity
    # alone would miss the old bug: its refundable and non-refundable amounts
    # added up correctly while some ODC was incorrectly refundable.
    np.testing.assert_allclose(total[baseline], r["total"][baseline])
    np.testing.assert_allclose(refundable[baseline], child_after_reductions[baseline])
    np.testing.assert_allclose(
        non_refundable[baseline], np.minimum(r["other"], r["total"])[baseline]
    )
    np.testing.assert_allclose(refundable + non_refundable, total)
    assert (refundable >= 0).all()
    assert (refundable <= child_after_reductions).all()
    assert (refundable[r["child"] == 0] == 0).all()
    # The stored non-refundable amount is before section 26(a), even where
    # the tax unit cannot use all its other-dependent credit.
    assert (baseline & (non_refundable > liability)).any()
    assert (baseline & (r["first"] > 0) & (r["other"] > 0) & (refundable > 0)).any()
    assert (
        baseline & (r["ordinary"] > 0) & (refundable == 0) & (non_refundable > 0)
    ).any()


def test_2021_preserves_lower_refundable_maximum(split_grid):
    simulation, references, baseline, _, _, _ = split_grid
    r = references[2021]
    expected = np.minimum(
        np.maximum(r["maximum"] - r["first"] - r["ordinary"], 0), r["total"]
    )
    actual = simulation.calculate("refundable_ctc", 2021)
    np.testing.assert_allclose(actual[~baseline], expected[~baseline])
    assert (actual <= r["maximum"]).all()
    assert ((~baseline) & (actual > 0) & (actual < r["child"])).any()


@pytest.mark.parametrize("year", OTHER_YEARS)
def test_other_years_preserve_partial_refundability(split_grid, year):
    simulation, references, _, phase_in, liability, barred = split_grid
    r = references[year]
    # The legacy section 24(d) calculation refunds the gain in allowed CTC
    # when its tax limit increases by the phase-in, subject to its child cap
    # and the separate section 911 bar.
    increase = np.minimum(r["total"], liability + phase_in) - np.minimum(
        r["total"], liability
    )
    expected = np.where(barred, 0, np.minimum(r["maximum"], increase))
    total = simulation.calculate("ctc", year)
    refundable = simulation.calculate("refundable_ctc", year)
    non_refundable = simulation.calculate("non_refundable_ctc", year)
    np.testing.assert_allclose(total, r["total"])
    np.testing.assert_allclose(refundable, expected)
    np.testing.assert_allclose(refundable + non_refundable, total)
    assert (refundable <= r["child"]).all()
    assert ((refundable > 0) & (refundable < total)).any()
    assert ((total > 0) & (refundable == 0)).any()
