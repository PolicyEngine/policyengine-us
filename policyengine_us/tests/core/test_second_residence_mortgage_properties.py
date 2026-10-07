"""Vectorized invariants for second-residence mortgage inputs and Kentucky.

One module fixture builds one Simulation of Kentucky tax units in 2025 and
2026, in four paired scenarios with identical draws:

- base: separate principal- and second-residence interest, points and premiums;
- pooled: every second-residence amount moved onto the principal residence;
- principal_only: second-residence inputs set to zero;
- omitted: second-residence inputs left out entirely.

Federal law pools both qualified residences (26 U.S.C. 163(h)(5)(A)), so the
federal deduction cannot depend on the residence split. KRS 141.019(2)(j)
limits Kentucky's deduction to the principal residence from 2026, so from
then on Kentucky itemized deductions cannot depend on second-residence
amounts at all.
"""

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.variables.household.expense.tax_unit.mortgage_interest_structure import (
    _limited_mortgage_balance,
    _mortgage_balance_cap,
)

N = 48
YEARS = (2025, 2026)
STATUSES = ("SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD")
SCENARIOS = ("base", "pooled", "principal_only", "omitted")
# Principal-residence input, its second-residence counterpart, upper draw.
PAIRS = (
    ("home_mortgage_interest", "second_residence_mortgage_interest", 40_000),
    ("home_mortgage_points", "second_residence_mortgage_points", 6_000),
    (
        "mortgage_insurance_premiums",
        "second_residence_mortgage_insurance_premiums",
        5_000,
    ),
)
UNIT_OUTPUTS = (
    "home_mortgage_interest_tax_unit",
    "deductible_mortgage_interest_tax_unit",
    "non_deductible_mortgage_interest_tax_unit",
    "deductible_mortgage_insurance_premiums",
    "interest_deduction",
    "second_residence_interest_deduction",
    "itemized_deductions_less_salt",
    "ky_disallowed_second_residence_interest",
    "ky_itemized_deductions_unit",
)
PERSON_OUTPUTS = (
    "home_mortgage_interest_share",
    "deductible_mortgage_interest",
    "mortgage_interest",
)
FEDERAL_UNIT_OUTPUTS = (
    "deductible_mortgage_interest_tax_unit",
    "non_deductible_mortgage_interest_tax_unit",
    "deductible_mortgage_insurance_premiums",
    "interest_deduction",
    "itemized_deductions_less_salt",
)
RTOL = 1e-6
ATOL = 0.01


def _close(actual, expected):
    np.testing.assert_allclose(actual, expected, rtol=RTOL, atol=ATOL)


def _draw():
    rng = np.random.default_rng(141_019)
    statuses = rng.choice(STATUSES, N)
    statuses[: 2 * len(STATUSES)] = np.tile(STATUSES, 2)
    spouse = statuses == "JOINT"
    amounts = {}
    for principal, second, upper in PAIRS:
        for name in (principal, second):
            amount = rng.integers(0, upper * 100 + 1, (N, 2)) / 100
            amount[rng.random((N, 2)) < 0.25] = 0
            amount[~spouse, 1] = 0
            amounts[name] = amount
    # Units with only second-residence interest, and with no mortgage at all.
    amounts["home_mortgage_interest"][::7] = 0
    for principal, second, _ in PAIRS:
        amounts[principal][::11] = 0
        amounts[second][::11] = 0
    first = rng.integers(1, 1_500_001, N).astype(float)
    second_balance = rng.integers(1, 750_001, N).astype(float)
    first[::5] = 0
    second_balance[::3] = 0
    # AGI on both sides of the premium phase-out range.
    agi = rng.integers(0, 15_000_001, N) / 100
    return {
        **amounts,
        "filing_status": statuses,
        "adjusted_gross_income": agi,
        "first_home_mortgage_balance": first,
        "second_home_mortgage_balance": second_balance,
        "first_home_mortgage_origination_year": rng.choice((2010, 2016, 2020), N),
        "second_home_mortgage_origination_year": rng.choice((2010, 2016, 2020), N),
    }


def _person_inputs(draws, scenario, i, j):
    inputs = {}
    for principal, second, _ in PAIRS:
        principal_value = float(draws[principal][i, j])
        second_value = float(draws[second][i, j])
        if scenario == "pooled":
            principal_value += second_value
            second_value = 0.0
        elif scenario in ("principal_only", "omitted"):
            second_value = 0.0
        inputs[principal] = principal_value
        if scenario != "omitted":
            inputs[second] = second_value
    return inputs


@pytest.fixture(scope="module")
def results():
    draws = _draw()
    people, tax_units, households = {}, {}, {}
    units, persons, person_to_unit = {}, {}, []
    periods = tuple(map(str, YEARS))

    def annual(value):
        return dict.fromkeys(periods, value)

    for scenario in SCENARIOS:
        units[scenario], persons[scenario] = [], []
        for i in range(N):
            unit_index = len(tax_units)
            units[scenario].append(unit_index)
            members = []
            count = 2 if draws["filing_status"][i] == "JOINT" else 1
            for j in range(count):
                person_index = len(people)
                persons[scenario].append(person_index)
                person_to_unit.append(unit_index)
                person_id = f"p{person_index}"
                members.append(person_id)
                person = {"age": annual(50 - j)}
                for name, value in _person_inputs(draws, scenario, i, j).items():
                    person[name] = annual(value)
                people[person_id] = person
            tax_units[f"t{unit_index}"] = {
                "members": members,
                "filing_status": annual(str(draws["filing_status"][i])),
                "adjusted_gross_income": annual(
                    float(draws["adjusted_gross_income"][i])
                ),
                "first_home_mortgage_balance": annual(
                    float(draws["first_home_mortgage_balance"][i])
                ),
                "second_home_mortgage_balance": annual(
                    float(draws["second_home_mortgage_balance"][i])
                ),
                "first_home_mortgage_origination_year": annual(
                    int(draws["first_home_mortgage_origination_year"][i])
                ),
                "second_home_mortgage_origination_year": annual(
                    int(draws["second_home_mortgage_origination_year"][i])
                ),
                # Keep the deprecated structured interest out of every pool.
                "first_home_mortgage_interest": annual(0.0),
                "second_home_mortgage_interest": annual(0.0),
            }
            households[f"h{unit_index}"] = {
                "members": members,
                "state_code": annual("KY"),
            }

    simulation = Simulation(
        situation={"people": people, "tax_units": tax_units, "households": households}
    )
    values = {}
    for year in YEARS:
        values[year] = {}
        for name in UNIT_OUTPUTS + PERSON_OUTPUTS:
            array = simulation.calculate(name, str(year)).copy()
            array.flags.writeable = False
            values[year][name] = array
        # Read the acquisition-debt caps once, from this model's parameters.
        mortgage = simulation.tax_benefit_system.parameters(
            f"{year}-01-01"
        ).gov.irs.deductions.itemized.interest.mortgage
        statuses = draws["filing_status"]
        values[year]["caps"] = (
            mortgage.pre_tcja_cap[statuses],
            mortgage.cap[statuses],
            mortgage.pre_tcja_origination_year,
        )
    # Do not retain the Simulation, its mutable caches or its policy tree.
    return (
        draws,
        values,
        {k: np.array(v) for k, v in units.items()},
        {k: np.array(v) for k, v in persons.items()},
        np.array(person_to_unit),
    )


def test_residence_split_does_not_change_federal_amounts(results):
    _, values, units, persons, _ = results
    for year_values in values.values():
        for name in FEDERAL_UNIT_OUTPUTS:
            _close(year_values[name][units["base"]], year_values[name][units["pooled"]])
        # Moving amounts within a person keeps that person's allocation.
        for name in PERSON_OUTPUTS:
            _close(
                year_values[name][persons["base"]],
                year_values[name][persons["pooled"]],
            )


def test_attribution_is_nonnegative_and_bounded(results):
    _, values, _, _, _ = results
    for year_values in values.values():
        attribution = year_values["second_residence_interest_deduction"]
        assert np.all(attribution >= 0)
        assert np.all(attribution <= year_values["interest_deduction"] + ATOL)


def test_attribution_equals_the_federal_deduction_it_adds(results):
    # Differential check: given balances and AGI the federal deduction is
    # linear in the amounts, so the attribution must equal the deduction
    # with second-residence amounts minus the deduction without them.
    _, values, units, _, _ = results
    for year_values in values.values():
        deduction = year_values["interest_deduction"]
        _close(
            deduction[units["base"]] - deduction[units["principal_only"]],
            year_values["second_residence_interest_deduction"][units["base"]],
        )


def test_attribution_matches_an_independent_computation(results):
    draws, values, units, _, _ = results
    statuses = draws["filing_status"]
    for year, year_values in values.items():
        caps = [
            _mortgage_balance_cap(
                draws[f"{position}_home_mortgage_origination_year"],
                *year_values["caps"],
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
        # Premium worksheet: 10% per $1,000 ($500 separate), or fraction,
        # above $100,000 ($50,000 separate); no premiums in 2022-2025.
        separate = statuses == "SEPARATE"
        start = np.where(separate, 50_000, 100_000)
        increment = np.where(separate, 500, 1_000)
        excess = np.maximum(0, draws["adjusted_gross_income"] - start)
        kept = 1 - np.minimum(1, np.ceil(excess / increment) * 0.1)
        kept = kept * (year != 2025)
        interest_and_points = draws["second_residence_mortgage_interest"].sum(
            axis=1
        ) + draws["second_residence_mortgage_points"].sum(axis=1)
        premiums = draws["second_residence_mortgage_insurance_premiums"].sum(axis=1)
        expected = interest_and_points * share + premiums * kept
        _close(
            values[year]["second_residence_interest_deduction"][units["base"]],
            expected,
        )


def test_kentucky_limits_qualified_residence_interest_from_2026(results):
    _, values, units, _, _ = results
    before, after = values[2025], values[2026]
    np.testing.assert_array_equal(before["ky_disallowed_second_residence_interest"], 0)
    # 2025: second-residence amounts raise Kentucky itemized deductions
    # one-for-one with the federal deduction they add.
    _close(
        before["ky_itemized_deductions_unit"][units["base"]]
        - before["ky_itemized_deductions_unit"][units["principal_only"]],
        before["second_residence_interest_deduction"][units["base"]],
    )
    # 2026: Kentucky removes exactly the second-residence part...
    _close(
        after["ky_disallowed_second_residence_interest"],
        after["second_residence_interest_deduction"],
    )
    # ...so its itemized deductions no longer depend on second-residence
    # amounts, while the federal deduction still does...
    _close(
        after["ky_itemized_deductions_unit"][units["base"]],
        after["ky_itemized_deductions_unit"][units["principal_only"]],
    )
    # ...and moving those amounts onto the principal residence restores them.
    pooled_gain = (
        after["ky_itemized_deductions_unit"][units["pooled"]]
        - after["ky_itemized_deductions_unit"][units["base"]]
    )
    _close(pooled_gain, after["second_residence_interest_deduction"][units["base"]])
    assert np.any(after["second_residence_interest_deduction"][units["base"]] > 0)


def test_omitted_and_zero_second_residence_inputs_match(results):
    _, values, units, persons, _ = results
    for year_values in values.values():
        for name in UNIT_OUTPUTS:
            np.testing.assert_array_equal(
                year_values[name][units["principal_only"]],
                year_values[name][units["omitted"]],
            )
        for name in PERSON_OUTPUTS:
            np.testing.assert_array_equal(
                year_values[name][persons["principal_only"]],
                year_values[name][persons["omitted"]],
            )
        np.testing.assert_array_equal(
            year_values["second_residence_interest_deduction"][units["omitted"]], 0
        )
        np.testing.assert_array_equal(
            year_values["ky_disallowed_second_residence_interest"][units["omitted"]],
            0,
        )
