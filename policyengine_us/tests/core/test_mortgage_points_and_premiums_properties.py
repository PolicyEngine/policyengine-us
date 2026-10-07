"""Vectorized mortgage invariants that household YAML examples cannot express.

One module fixture builds one Simulation for 360 tax units in 2021, 2025 and
2026. Seeded draws and paired tax units exercise conservation, bounds,
interest/points transfers, an independent integer-cents Schedule A worksheet,
AGI monotonicity and compatibility with zero or omitted new inputs. Paired
units avoid changing inputs or sharing mutable simulations between tests;
the fixture exposes only read-only arrays after calculation.

Reference: 2021 Instructions for Schedule A, Mortgage Insurance Premiums
Deduction Worksheet, lines 1-7 (page A-10), and Publication 936, Table 1,
line 13 instructions. YAML covers the individual thresholds and 2022-2024.
"""

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.variables.household.expense.tax_unit.mortgage_interest_structure import (
    _limited_mortgage_balance,
    _mortgage_balance_cap,
)

N = 60
YEARS = (2021, 2025, 2026)
STATUSES = ("SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE")
SCENARIOS = ("base", "moved", "richer", "zero", "omitted", "legacy")
PERSON_INPUTS = (
    "home_mortgage_interest",
    "home_mortgage_points",
    "mortgage_insurance_premiums",
    "investment_interest_expense",
)
PERSON_OUTPUTS = (
    "home_mortgage_interest_share",
    "deductible_mortgage_interest",
    "non_deductible_mortgage_interest",
    "mortgage_interest",
    "deductible_interest_expense",
)
UNIT_OUTPUTS = (
    "home_mortgage_interest_tax_unit",
    "deductible_mortgage_interest_tax_unit",
    "non_deductible_mortgage_interest_tax_unit",
    "deductible_mortgage_insurance_premiums",
    "interest_deduction",
)
# Mortgage outputs are float32. Allow accumulated rounding in person sums
# and transfers, scaling with the operands, not with a small difference.
RTOL = 1e-6
ATOL = 0.01


def _close(actual, expected):
    np.testing.assert_allclose(actual, expected, rtol=RTOL, atol=ATOL)


def _draw():
    rng = np.random.default_rng(936_2021)
    statuses = rng.choice(STATUSES, N)
    statuses[: 3 * len(STATUSES)] = np.tile(STATUSES, 3)
    spouse = statuses == "JOINT"
    start_cents = np.where(statuses == "SEPARATE", 5_000_000, 10_000_000)
    increment_cents = np.where(statuses == "SEPARATE", 50_000, 100_000)
    agi_cents = rng.integers(0, 15_000_001, N)
    # Include exact multiples and one cent on either side of increments.
    boundary = np.arange(N) % 3 != 2
    steps = rng.integers(0, 12, N)
    offsets = rng.choice((-1, 0, 1), N)
    agi_cents[boundary] = (start_cents + steps * increment_cents + offsets)[boundary]
    # Guarantee an exact increment and nearby cents in every filing status.
    for block, (step, offset) in enumerate(((1, 0), (1, 1), (9, -1))):
        rows = slice(block * len(STATUSES), (block + 1) * len(STATUSES))
        agi_cents[rows] = start_cents[rows] + step * increment_cents[rows] + offset
    inputs = {}
    for name, upper in zip(PERSON_INPUTS, (40_000, 10_000, 12_000, 4_000)):
        # Integer premiums make the independent worksheet entirely integer
        # arithmetic through line 7; other expenses include cents.
        if name == "mortgage_insurance_premiums":
            amount = rng.integers(0, upper + 1, (N, 2)).astype(float)
        else:
            amount = rng.integers(0, upper * 100 + 1, (N, 2)) / 100
        amount[rng.random((N, 2)) < 0.2] = 0
        amount[~spouse, 1] = 0
        inputs[name] = amount
    # Exercise zero-interest, points-only and all-zero mortgage pools.
    inputs["home_mortgage_interest"][::5] = 0
    inputs["home_mortgage_points"][::10] = 0
    first = rng.integers(1, 1_500_001, N).astype(float)
    second = rng.integers(1, 750_001, N).astype(float)
    first[::6] = 0
    second[::3] = 0
    transfer_fraction = rng.uniform(0, 1, (N, 2))
    # Include complete transfers, so interest can vanish and invoke fallback.
    transfer_fraction[::3] = 0
    transfer_fraction[1::3] = 1
    return {
        **inputs,
        "filing_status": statuses,
        "adjusted_gross_income": agi_cents / 100,
        "agi_cents": agi_cents,
        "raised_agi_cents": agi_cents + rng.integers(1, 2_000_001, N),
        "first_home_mortgage_balance": first,
        "second_home_mortgage_balance": second,
        "first_home_mortgage_origination_year": rng.choice((2010, 2016, 2020), N),
        "second_home_mortgage_origination_year": rng.choice((2010, 2016, 2020), N),
        "transfer_fraction": transfer_fraction,
    }


@pytest.fixture(scope="module")
def mortgage_results():
    draws = _draw()
    people, tax_units, households = {}, {}, {}
    unit_indices, person_indices, person_to_unit = {}, {}, []
    periods = tuple(map(str, YEARS))

    def annual(value):
        return dict.fromkeys(periods, value)

    for scenario in SCENARIOS:
        unit_indices[scenario], person_indices[scenario] = [], []
        for i in range(N):
            unit_index = len(tax_units)
            unit_indices[scenario].append(unit_index)
            members = []
            count = 2 if draws["filing_status"][i] == "JOINT" else 1
            for j in range(count):
                person_index = len(people)
                person_indices[scenario].append(person_index)
                person_to_unit.append(unit_index)
                person_id = f"p{person_index}"
                members.append(person_id)
                person = {"age": annual(50 - j)}
                total = sum(draws[name][i, j] for name in PERSON_INPUTS[:2])
                for name in PERSON_INPUTS:
                    value = float(draws[name][i, j])
                    if scenario == "moved":
                        fraction = draws["transfer_fraction"][i, j]
                        if name == "home_mortgage_interest":
                            value = total * fraction
                        elif name == "home_mortgage_points":
                            value = total * (1 - fraction)
                    if scenario in ("zero", "omitted", "legacy") and name in (
                        "home_mortgage_points",
                        "mortgage_insurance_premiums",
                    ):
                        if scenario == "omitted":
                            continue
                        value = 0.0
                    if scenario == "legacy" and name == "home_mortgage_interest":
                        value = 0.0
                    person[name] = annual(value)
                people[person_id] = person
            unit = {
                "members": members,
                "filing_status": annual(str(draws["filing_status"][i])),
                "adjusted_gross_income": annual(
                    float(
                        draws[
                            "raised_agi_cents" if scenario == "richer" else "agi_cents"
                        ][i]
                        / 100
                    )
                ),
                **{
                    name: annual(float(draws[name][i]))
                    for name in (
                        "first_home_mortgage_balance",
                        "second_home_mortgage_balance",
                    )
                },
                **{
                    name: annual(int(draws[name][i]))
                    for name in (
                        "first_home_mortgage_origination_year",
                        "second_home_mortgage_origination_year",
                    )
                },
                # The transfer property must not trigger the legacy fallback.
                "first_home_mortgage_interest": annual(0.0),
                "second_home_mortgage_interest": annual(0.0),
            }
            if scenario == "legacy":
                interest = draws["home_mortgage_interest"][i].sum()
                unit["first_home_mortgage_interest"] = annual(float(interest * 0.6))
                unit["second_home_mortgage_interest"] = annual(float(interest * 0.4))
            tax_units[f"t{unit_index}"] = unit
            households[f"h{unit_index}"] = {"members": members}

    simulation = Simulation(
        situation={"people": people, "tax_units": tax_units, "households": households}
    )
    results = {}
    for year in YEARS:
        results[year] = {}
        for name in UNIT_OUTPUTS + PERSON_OUTPUTS + PERSON_INPUTS:
            values = simulation.calculate(name, str(year)).copy()
            values.flags.writeable = False
            results[year][name] = values
        # Reuse only the unchanged pre-input balance helpers to reconstruct
        # the previous mortgage computation, with no points or premium term.
        p = simulation.tax_benefit_system.parameters(
            f"{year}-01-01"
        ).gov.irs.deductions.itemized.interest.mortgage
        pre_cap = p.pre_tcja_cap[draws["filing_status"]]
        post_cap = p.cap[draws["filing_status"]]
        caps = [
            _mortgage_balance_cap(
                draws[f"{position}_home_mortgage_origination_year"],
                pre_cap,
                post_cap,
                p.pre_tcja_origination_year,
            )
            for position in ("first", "second")
        ]
        first = draws["first_home_mortgage_balance"]
        second = draws["second_home_mortgage_balance"]
        limited = _limited_mortgage_balance(first, second, *caps)
        share = np.minimum(
            1,
            np.divide(
                limited, first + second, out=np.ones(N), where=first + second > 0
            ),
        )
        share.flags.writeable = False
        results[year]["legacy_deductible_share"] = share
    # Do not retain the Simulation, its mutable caches or its policy tree.
    return draws, results, unit_indices, person_indices, np.array(person_to_unit)


def _sum_people(values, person_to_unit):
    return np.bincount(person_to_unit, weights=values, minlength=N * len(SCENARIOS))


def test_mortgage_pool_and_person_allocations_are_conserved(mortgage_results):
    _, results, _, _, membership = mortgage_results
    for values in results.values():
        pool = values["home_mortgage_interest_tax_unit"] + _sum_people(
            values["home_mortgage_points"], membership
        )
        deductible = values["deductible_mortgage_interest_tax_unit"]
        nondeductible = values["non_deductible_mortgage_interest_tax_unit"]
        _close(deductible + nondeductible, pool)
        _close(
            _sum_people(values["deductible_mortgage_interest"], membership), deductible
        )
        _close(
            _sum_people(values["non_deductible_mortgage_interest"], membership),
            nondeductible,
        )
        _close(_sum_people(values["mortgage_interest"], membership), pool)


def test_outputs_are_nonnegative_and_deductions_are_bounded(mortgage_results):
    _, results, _, _, membership = mortgage_results
    for values in results.values():
        for name in UNIT_OUTPUTS + PERSON_OUTPUTS:
            assert np.all(values[name] >= 0), name
        pool = values["home_mortgage_interest_tax_unit"] + _sum_people(
            values["home_mortgage_points"], membership
        )
        assert np.all(values["deductible_mortgage_interest_tax_unit"] <= pool + ATOL)
        premiums = _sum_people(values["mortgage_insurance_premiums"], membership)
        assert np.all(values["deductible_mortgage_insurance_premiums"] <= premiums)


def test_points_and_interest_are_interchangeable(mortgage_results):
    _, results, units, persons, _ = mortgage_results
    for values in results.values():
        for name in (
            "deductible_mortgage_interest_tax_unit",
            "non_deductible_mortgage_interest_tax_unit",
        ):
            _close(values[name][units["moved"]], values[name][units["base"]])
        # Moving amounts within a person also preserves their allocation.
        for name in ("deductible_mortgage_interest", "mortgage_interest"):
            _close(values[name][persons["moved"]], values[name][persons["base"]])


def _premium_worksheet_cents(premiums_cents, agi_cents, statuses):
    """2021 Schedule A lines 1-7, independently using integer cents.

    Line 4 rounds excess AGI UP to a $1,000/$500 multiple; line 5 divides
    that rounded dollar excess by $10,000/$5,000, capped at 1. Lines 6-7
    multiply premiums by the fraction and subtract the reduction.
    """
    deductions = []
    for line_1, line_2, status in zip(premiums_cents, agi_cents, statuses):
        separate = status == "SEPARATE"
        line_3 = 5_000_000 if separate else 10_000_000
        if line_2 <= line_3:
            deductions.append(int(line_1))
            continue
        multiple = 50_000 if separate else 100_000
        line_4 = ((int(line_2) - line_3 + multiple - 1) // multiple) * multiple
        denominator = 500_000 if separate else 1_000_000
        numerator = min(line_4, denominator)
        line_6 = int(line_1) * numerator // denominator
        deductions.append(int(line_1) - line_6)
    return np.array(deductions)


def test_premiums_match_the_independent_integer_worksheet(mortgage_results):
    draws, results, units, _, membership = mortgage_results
    for year, values in results.items():
        premiums_cents = np.rint(
            _sum_people(values["mortgage_insurance_premiums"], membership) * 100
        ).astype(np.int64)
        for scenario in SCENARIOS:
            indices = units[scenario]
            agi = draws["raised_agi_cents" if scenario == "richer" else "agi_cents"]
            expected = (
                _premium_worksheet_cents(
                    premiums_cents[indices], agi, draws["filing_status"]
                )
                / 100
            )
            if year == 2025:
                expected = np.zeros(N)
            _close(values["deductible_mortgage_insurance_premiums"][indices], expected)


def test_premium_deduction_never_increases_with_agi(mortgage_results):
    _, results, units, _, _ = mortgage_results
    for year, values in results.items():
        premiums = values["deductible_mortgage_insurance_premiums"]
        assert np.all(premiums[units["richer"]] <= premiums[units["base"]])
        if year != 2025:
            assert np.any(premiums[units["richer"]] < premiums[units["base"]])


def test_zero_new_inputs_preserve_the_previous_computation(mortgage_results):
    _, results, units, persons, membership = mortgage_results
    for values in results.values():
        for name in UNIT_OUTPUTS:
            np.testing.assert_array_equal(
                values[name][units["zero"]], values[name][units["omitted"]]
            )
        for name in PERSON_OUTPUTS:
            np.testing.assert_array_equal(
                values[name][persons["zero"]], values[name][persons["omitted"]]
            )
        for scenario in ("zero", "omitted", "legacy"):
            index = units[scenario]
            person_index = persons[scenario]
            interest = values["home_mortgage_interest_tax_unit"][index]
            person_interest = values["home_mortgage_interest"][person_index]
            totals = _sum_people(values["home_mortgage_interest"], membership)[index]
            local_membership = membership[person_index] - index[0]
            filer_count = np.bincount(local_membership, minlength=N)
            allocation = np.divide(
                person_interest,
                totals[local_membership],
                out=1.0 / filer_count[local_membership],
                where=totals[local_membership] > 0,
            )
            _close(values["home_mortgage_interest_share"][person_index], allocation)
            deductible = values["deductible_mortgage_interest_tax_unit"][index]
            nondeductible = values["non_deductible_mortgage_interest_tax_unit"][index]
            _close(deductible, interest * values["legacy_deductible_share"])
            _close(deductible + nondeductible, interest)
            _close(
                values["deductible_mortgage_interest"][person_index],
                deductible[local_membership] * allocation,
            )
            _close(
                values["non_deductible_mortgage_interest"][person_index],
                nondeductible[local_membership] * allocation,
            )
            _close(
                values["mortgage_interest"][person_index],
                interest[local_membership] * allocation,
            )
            previous_interest = _sum_people(
                values["deductible_interest_expense"], membership
            )[index]
            _close(values["interest_deduction"][index], previous_interest)
            np.testing.assert_array_equal(
                values["deductible_mortgage_insurance_premiums"][index], np.zeros(N)
            )
