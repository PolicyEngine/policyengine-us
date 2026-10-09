"""Differential tests for the IRA rules in 26 U.S.C. 219(b), (c), and (g).

Each batch is an ordinary situation containing independent households. These
tests compare the vectorized model with a Decimal implementation of the law,
using the amounts published in IRS Notices 2014-70, 2015-75, 2016-62, 2017-64,
2018-83, 2019-59, 2020-79, 2021-61, 2022-55, 2023-75, 2024-80, and 2025-67.
No model parameters or formula helpers supply the expected results.

The grids check that deductible dollar limits fall with MAGI, are rounded in
$10 increments, retain the $200 floor until complete phase-out, and distinguish
own participation from a spouse's participation. Contribution grids check
individual dollar limits, joint compensation conservation, role symmetry,
the strict lower-compensation rule, proportional allocation, and exclusion of
dependent contributions from the filers' deduction.
"""

from decimal import Decimal, ROUND_FLOOR
from itertools import product

import numpy as np
import pytest

from policyengine_us import Simulation


# Year: (active single start, active joint start, nonactive spouse start,
#        ordinary dollar limit, age-50 catch-up).
NOTICE_AMOUNTS = {
    2015: (61_000, 98_000, 183_000, 5_500, 1_000),
    2016: (61_000, 98_000, 184_000, 5_500, 1_000),
    2017: (62_000, 99_000, 186_000, 5_500, 1_000),
    2018: (63_000, 101_000, 189_000, 5_500, 1_000),
    2019: (64_000, 103_000, 193_000, 6_000, 1_000),
    2020: (65_000, 104_000, 196_000, 6_000, 1_000),
    2021: (66_000, 105_000, 198_000, 6_000, 1_000),
    2022: (68_000, 109_000, 204_000, 6_000, 1_000),
    2023: (73_000, 116_000, 218_000, 6_500, 1_000),
    2024: (77_000, 123_000, 230_000, 7_000, 1_000),
    2025: (79_000, 126_000, 236_000, 7_000, 1_000),
    2026: (81_000, 129_000, 242_000, 7_500, 1_100),
}


def blank_situation():
    return {
        entity: {}
        for entity in (
            "people",
            "marital_units",
            "tax_units",
            "spm_units",
            "families",
            "households",
        )
    }


def add_household(
    situation, tag, year, person_inputs, tax_inputs, *, couple=False, separate=False
):
    """Add a household, returning its persons' positions in calculated arrays."""
    positions = []
    names = []
    for index, inputs in enumerate(person_inputs):
        name = f"{tag}_p{index}"
        positions.append(len(situation["people"]))
        names.append(name)
        values = {
            "age": 40,
            "is_tax_unit_head": index == 0 or (separate and index == 1),
            "is_tax_unit_spouse": couple and not separate and index == 1,
            "is_tax_unit_dependent": index >= 2,
            **inputs,
        }
        situation["people"][name] = {
            variable: {year: value} for variable, value in values.items()
        }
    if separate:
        for index, name in enumerate(names):
            situation["tax_units"][f"{tag}_t{index}"] = {
                "members": [name],
                **{variable: {year: value} for variable, value in tax_inputs.items()},
            }
    else:
        situation["tax_units"][f"{tag}_t"] = {
            "members": names,
            **{variable: {year: value} for variable, value in tax_inputs.items()},
        }
    groups = [names[:2]] if couple else []
    groups += [[name] for name in names[2 if couple else 0 :]]
    for index, members in enumerate(groups):
        situation["marital_units"][f"{tag}_m{index}"] = {"members": members}
    for entity in ("spm_units", "families", "households"):
        situation[entity][tag] = {"members": names}
    situation["households"][tag]["state_code"] = {year: "TX"}
    return positions


def statutory_phase_out(year, status, active, spouse_active, cohabitating):
    """Return the applicable range, or None if section 219(g) does not apply."""
    single_start, joint_start, spouse_start, _, _ = NOTICE_AMOUNTS[year]
    if status == "SEPARATE":
        if cohabitating:
            return (0, 10_000) if active or spouse_active else None
        return (single_start, 10_000) if active else None
    if active:
        if status in ("JOINT", "SURVIVING_SPOUSE"):
            return joint_start, 20_000
        return single_start, 10_000
    if status == "JOINT" and spouse_active:
        return spouse_start, 10_000
    return None


def decimal_deductible_limit(limit, magi, phase_out):
    """Apply 219(g)(2) directly, rounding the reduction downward to $10."""
    if phase_out is None:
        return limit
    start, width = map(Decimal, phase_out)
    excess = max(Decimal(0), Decimal(str(magi)) - start)
    if excess >= width:
        return 0
    reduction = Decimal(limit) * excess / width
    rounded_reduction = (reduction / 10).to_integral_value(rounding=ROUND_FLOOR) * 10
    return float(max(Decimal(200), Decimal(limit) - rounded_reduction))


@pytest.mark.parametrize("year", NOTICE_AMOUNTS)
def test_phase_out_matches_statute_across_statuses_and_years(year):
    routes = [
        ("SINGLE", True, False, False),
        ("HEAD_OF_HOUSEHOLD", True, False, False),
        ("SURVIVING_SPOUSE", True, False, False),
        ("JOINT", True, False, False),
        ("JOINT", True, True, False),
        ("JOINT", False, True, False),
        ("JOINT", False, False, False),
        ("SEPARATE", True, False, True),
        ("SEPARATE", False, True, True),
        ("SEPARATE", False, False, True),
        ("SEPARATE", True, True, False),
        ("SEPARATE", False, True, False),
    ]
    situation = blank_situation()
    expected, target_positions, dollar_limits, groups = [], [], [], []
    for route, age in product(routes, (49, 50)):
        status, active, spouse_active, cohabitating = route
        phase_out = statutory_phase_out(year, *route)
        start, width = phase_out or (NOTICE_AMOUNTS[year][0], 10_000)
        limit = NOTICE_AMOUNTS[year][3] + (NOTICE_AMOUNTS[year][4] if age >= 50 else 0)
        offsets = [
            -1,
            0,
            1,
            25,
            width // 3,
            width // 2,
            width - 301,
            width - 251,
            width - 1,
            width,
            width + 1,
        ]
        group = []
        for offset in offsets:
            magi = start + offset
            people = [{"age": age, "ira_active_participant": active}]
            couple = status in ("JOINT", "SEPARATE")
            if couple:
                people.append({"age": age, "ira_active_participant": spouse_active})
            positions = add_household(
                situation,
                f"case{len(expected)}",
                year,
                people,
                {
                    "filing_status": status,
                    "cohabitating_spouses": cohabitating,
                    "ira_219g_magi": magi,
                },
                couple=couple,
                separate=status == "SEPARATE",
            )
            group.append(len(expected))
            target_positions.append(positions[0])
            dollar_limits.append(limit)
            expected.append(decimal_deductible_limit(limit, magi, phase_out))
        groups.append(group)
    simulation = Simulation(situation=situation)
    actual = simulation.calculate("ira_219g_deductible_limit", year)[target_positions]
    np.testing.assert_allclose(actual, expected, rtol=0, atol=0.01)
    assert np.all(actual >= 0)
    assert np.all(actual <= dollar_limits)
    assert np.all((actual == 0) | (actual >= 200))
    np.testing.assert_allclose(actual % 10, 0, rtol=0, atol=0.01)
    for group in groups:
        assert np.all(np.diff(actual[group]) <= 0), "deductible limit rose with MAGI"


def reference_joint_contributions(compensation, desired, dollar_limits):
    """219(c)(2) applies only to the spouse with strictly less compensation."""
    contributions = [
        min(compensation[index], desired[index], dollar_limits[index])
        for index in (0, 1)
    ]
    for index in (0, 1):
        spouse = 1 - index
        if compensation[index] < compensation[spouse]:
            available = compensation[index] + max(
                compensation[spouse] - contributions[spouse], 0
            )
            contributions[index] = min(available, desired[index], dollar_limits[index])
    return contributions


def test_joint_contributions_conserve_compensation_and_exclude_dependents():
    year = 2026
    compensation_grid = (0, 0.5, 1_000, 3_500, 7_500, 10_000)
    allocations = ((0, 0), (0.25, 0.25), (1_000, 0), (0, 7_000), (20_000, 20_000))
    situation = blank_situation()
    expected, desired_traditional, desired_total, compensation_total = [], [], [], []
    swapped_cases = {}
    dollar_limits = (7_500, 7_500)
    for case, (head_comp, spouse_comp, head_allocation, spouse_allocation) in enumerate(
        product(compensation_grid, compensation_grid, allocations, allocations)
    ):
        compensation = (head_comp, spouse_comp)
        total_desired = tuple(
            sum(values) for values in (head_allocation, spouse_allocation)
        )
        contribution = reference_joint_contributions(
            compensation, total_desired, dollar_limits
        )
        people = []
        for comp, allocation in zip(compensation, (head_allocation, spouse_allocation)):
            people.append(
                {
                    "ira_compensation": comp,
                    "traditional_ira_contributions_desired": allocation[0],
                    "roth_ira_contributions_desired": allocation[1],
                }
            )
        # A working dependent has lawful IRA contributions on their own return.
        people.append(
            {
                "age": 17,
                "ira_compensation": 2_000,
                "traditional_ira_contributions_desired": 1_000,
                "roth_ira_contributions_desired": 500,
            }
        )
        add_household(
            situation,
            f"case{case}",
            year,
            people,
            {"filing_status": "JOINT", "ira_219g_magi": 0},
            couple=True,
        )
        expected.extend([*contribution, 1_500])
        desired_traditional.extend([head_allocation[0], spouse_allocation[0], 1_000])
        desired_total.extend([*total_desired, 1_500])
        compensation_total.append(sum(compensation))
        swapped_cases[(head_comp, spouse_comp, head_allocation, spouse_allocation)] = (
            case
        )
    simulation = Simulation(situation=situation)
    traditional = simulation.calculate("traditional_ira_contributions", year)
    roth = simulation.calculate("roth_ira_contributions", year)
    total = traditional + roth
    deduction = simulation.calculate("traditional_ira_deduction", year)
    np.testing.assert_allclose(total, expected, rtol=1e-6, atol=0.001)
    assert np.all(total >= 0)
    assert np.all(total <= 7_500.01)
    assert np.all(total <= np.array(desired_total) + 0.01)
    contributions = total.reshape(-1, 3)
    assert np.all(
        contributions[:, :2].sum(axis=1) <= np.array(compensation_total) + 0.01
    )
    np.testing.assert_allclose(deduction.reshape(-1, 3)[:, 2], 0, rtol=0, atol=0)
    np.testing.assert_allclose(
        deduction.reshape(-1, 3)[:, :2], traditional.reshape(-1, 3)[:, :2]
    )
    # Preserve the existing allocation of contributions between IRA types.
    expected_traditional = np.divide(
        np.array(expected) * desired_traditional,
        desired_total,
        out=np.zeros(len(expected)),
        where=np.array(desired_total) > 0,
    )
    np.testing.assert_allclose(traditional, expected_traditional, rtol=1e-6, atol=0.001)
    for (
        head_comp,
        spouse_comp,
        head_allocation,
        spouse_allocation,
    ), case in swapped_cases.items():
        swapped = swapped_cases[
            (spouse_comp, head_comp, spouse_allocation, head_allocation)
        ]
        np.testing.assert_allclose(
            contributions[case, :2], contributions[swapped, 1::-1]
        )


def test_compensation_excludes_net_self_employment_losses():
    year = 2026
    situation = blank_situation()
    expected = []
    for case, (wages, net_earnings, deductible_tax, retirement) in enumerate(
        product((0, 0.5, 1_000, 20_000), (-5_000, 0, 10_000), (0, 500), (0, 2_000))
    ):
        add_household(
            situation,
            f"case{case}",
            year,
            [
                {
                    "irs_employment_income": wages,
                    "self_employment_income": net_earnings / 4,
                    "sstb_self_employment_income": net_earnings / 4,
                    "farm_operations_income": net_earnings / 4,
                    "partnership_self_employment_net_earnings": net_earnings / 4,
                    "self_employment_tax_ald_person": deductible_tax,
                    "self_employed_pension_contribution_ald_person": retirement,
                }
            ],
            {"filing_status": "SINGLE"},
        )
        expected.append(wages + max(net_earnings - deductible_tax - retirement, 0))
    simulation = Simulation(situation=situation)
    np.testing.assert_allclose(
        simulation.calculate("ira_compensation", year), expected, rtol=0, atol=0.001
    )


def test_supplied_contributions_consume_the_limit_before_generated_ones():
    """Actual IRA contributions supplied as inputs use up compensation first.

    26 U.S.C. 219(c)(1)(B) reduces the lower-compensation spouse's limit by the
    other spouse's deductible and Roth contributions, and 408A(c)(2) shares one
    dollar limit between a person's traditional and Roth contributions. So a
    supplied Roth amount leaves only the remainder for generated contributions,
    whether it is the spouse's or the person's own.
    """
    year = 2026
    dollar_limit = 7_500
    situation = blank_situation()
    expected_spouse, conserved = [], []
    head_compensation = (0, 5_000, 10_000, 20_000)
    supplied_roth = (0, 2_000, 7_000, 9_000)
    for case, (comp, roth) in enumerate(product(head_compensation, supplied_roth)):
        add_household(
            situation,
            f"couple{case}",
            year,
            [
                {"ira_compensation": comp, "roth_ira_contributions": roth},
                {
                    "ira_compensation": 0,
                    "roth_ira_contributions": 0,
                    "traditional_ira_contributions_desired": 7_500,
                },
            ],
            {"filing_status": "JOINT", "ira_219g_magi": 0},
            couple=True,
        )
        # The spouse has no compensation, so only the spousal rule can apply,
        # and only when the other spouse has compensation to share.
        expected_spouse.append(min(7_500, dollar_limit, max(0, comp - roth)))
        conserved.append(roth <= comp)
    singles = (0, 2_000, 7_500)
    for case, roth in enumerate(singles):
        add_household(
            situation,
            f"single{case}",
            year,
            [
                {
                    "ira_compensation": 20_000,
                    "roth_ira_contributions": roth,
                    "traditional_ira_contributions_desired": 7_500,
                }
            ],
            {"filing_status": "SINGLE", "ira_219g_magi": 0},
        )
    simulation = Simulation(situation=situation)
    traditional = simulation.calculate("traditional_ira_contributions", year)
    roth = simulation.calculate("roth_ira_contributions", year)
    couples = len(head_compensation) * len(supplied_roth)
    couple_traditional = traditional[: 2 * couples].reshape(-1, 2)
    couple_roth = roth[: 2 * couples].reshape(-1, 2)
    np.testing.assert_allclose(couple_traditional[:, 1], expected_spouse, atol=0.001)
    np.testing.assert_allclose(couple_traditional[:, 0], 0, atol=0)
    # Joint contributions never exceed joint compensation when the supplied
    # amount itself fits within it.
    totals = couple_traditional.sum(axis=1) + couple_roth.sum(axis=1)
    compensation = np.repeat(head_compensation, len(supplied_roth))
    assert np.all(
        totals[np.array(conserved)] <= compensation[np.array(conserved)] + 0.01
    )
    single_traditional = traditional[2 * couples :]
    np.testing.assert_allclose(
        single_traditional, [dollar_limit - s for s in singles], atol=0.001
    )


def test_contributions_set_after_construction_count_as_supplied():
    """A contribution given through set_input is supplied, not generated.

    YAML tests pass inputs at construction, so this needs the simulation API.
    A single filer with $20,000 of compensation sets a $2,000 Roth
    contribution after the simulation is built; the $7,500 limit then leaves
    $5,500 for the desired traditional contribution (26 U.S.C. 408A(c)(2)).
    """
    year = 2026
    situation = blank_situation()
    add_household(
        situation,
        "single",
        year,
        [{"ira_compensation": 20_000, "traditional_ira_contributions_desired": 7_500}],
        {"filing_status": "SINGLE", "ira_219g_magi": 0},
    )
    simulation = Simulation(situation=situation)
    simulation.set_input("roth_ira_contributions", year, np.array([2_000.0]))
    traditional = simulation.calculate("traditional_ira_contributions", year)
    roth = simulation.calculate("roth_ira_contributions", year)
    np.testing.assert_allclose(traditional, [5_500], atol=0.001)
    np.testing.assert_allclose(roth, [2_000], atol=0)
