"""Vectorized invariants for second-residence mortgage inputs and Kentucky.

One module fixture builds one Simulation of Kentucky tax units in 2025 and
2026. Four paired scenarios share identical draws:

- base: separate principal- and second-residence interest, points and premiums;
- pooled: every second-residence amount moved onto the principal residence;
- principal_only: second-residence inputs set to zero;
- omitted: second-residence inputs left out entirely.

A fifth scenario, equal_rate, gives each tax unit a principal and a second
mortgage at one common rate, so the result can be checked against an
independent recomputation on the principal residence alone.

Federal law pools both qualified residences (26 U.S.C. 163(h)(5)(A)), so the
federal deduction cannot depend on the residence split. From 2026, KRS
141.019(2)(j) caps Kentucky's deduction at the interest paid on the
principal residence.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

N = 48
YEARS = (2025, 2026)
STATUSES = ("SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD")
SCENARIOS = ("base", "pooled", "principal_only", "omitted", "equal_rate")
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
# 26 U.S.C. 163(h)(3)(F)(i)(II): $750,000 ($375,000 married filing
# separately) for debt incurred after December 15, 2017.
POST_2017_LIMIT = {"SEPARATE": 375_000}
DEFAULT_POST_2017_LIMIT = 750_000
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
    # Every fourth unit reports no balances, so the pool is fully deductible.
    first[::4] = 0
    second_balance[::4] = 0
    # Equal-rate units: principal debt on the first loan, second-residence
    # debt on the second, both incurred after 2017 at one rate.
    equal_principal = rng.integers(1, 1_200_001, N).astype(float)
    equal_second = rng.integers(0, 800_001, N).astype(float)
    equal_rate = rng.uniform(0.02, 0.09, N)
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
        "equal_principal": equal_principal,
        "equal_second": equal_second,
        "equal_rate": equal_rate,
    }


def _person_inputs(draws, scenario, i, j):
    if scenario == "equal_rate":
        if j > 0:
            return {}
        return {
            "home_mortgage_interest": float(
                draws["equal_rate"][i] * draws["equal_principal"][i]
            ),
            "second_residence_mortgage_interest": float(
                draws["equal_rate"][i] * draws["equal_second"][i]
            ),
        }
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


def _balances(draws, scenario, i):
    if scenario == "equal_rate":
        return {
            "first_home_mortgage_balance": float(draws["equal_principal"][i]),
            "second_home_mortgage_balance": float(draws["equal_second"][i]),
            "first_home_mortgage_origination_year": 2020,
            "second_home_mortgage_origination_year": 2020,
        }
    return {
        name: (float if "balance" in name else int)(draws[name][i])
        for name in (
            "first_home_mortgage_balance",
            "second_home_mortgage_balance",
            "first_home_mortgage_origination_year",
            "second_home_mortgage_origination_year",
        )
    }


@pytest.fixture(scope="module")
def results():
    draws = _draw()
    people, tax_units, households = {}, {}, {}
    units, persons = {}, {}
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
                **{
                    name: annual(value)
                    for name, value in _balances(draws, scenario, i).items()
                },
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
    # Do not retain the Simulation, its mutable caches or its policy tree.
    return (
        draws,
        values,
        {k: np.array(v) for k, v in units.items()},
        {k: np.array(v) for k, v in persons.items()},
    )


def test_residence_split_does_not_change_federal_amounts(results):
    _, values, units, persons = results
    for year_values in values.values():
        for name in FEDERAL_UNIT_OUTPUTS:
            _close(year_values[name][units["base"]], year_values[name][units["pooled"]])
        # Moving amounts within a person keeps that person's allocation.
        for name in PERSON_OUTPUTS:
            _close(
                year_values[name][persons["base"]],
                year_values[name][persons["pooled"]],
            )


def test_kentucky_disallowance_is_bounded(results):
    _, values, _, _ = results
    np.testing.assert_array_equal(
        values[2025]["ky_disallowed_second_residence_interest"], 0
    )
    disallowed = values[2026]["ky_disallowed_second_residence_interest"]
    assert np.all(disallowed >= 0)
    assert np.all(disallowed <= values[2026]["interest_deduction"] + ATOL)
    assert np.any(disallowed > 0)


def test_kentucky_lies_between_principal_only_and_pooled(results):
    # Adding second-residence amounts cannot lower Kentucky's deduction, and
    # moving them onto the principal residence cannot lower it either.
    _, values, units, _ = results
    kentucky = values[2026]["ky_itemized_deductions_unit"]
    assert np.all(kentucky[units["principal_only"]] <= kentucky[units["base"]] + ATOL)
    assert np.all(kentucky[units["base"]] <= kentucky[units["pooled"]] + ATOL)


def test_kentucky_ignores_second_residence_when_the_pool_is_fully_deductible(
    results,
):
    draws, values, units, _ = results
    no_balance = (draws["first_home_mortgage_balance"] == 0) & (
        draws["second_home_mortgage_balance"] == 0
    )
    assert no_balance.sum() >= N // 4
    kentucky = values[2026]["ky_itemized_deductions_unit"]
    _close(
        kentucky[units["base"]][no_balance],
        kentucky[units["principal_only"]][no_balance],
    )


def test_kentucky_matches_a_principal_residence_recomputation_at_equal_rates(
    results,
):
    # Independent statutory computation: with one rate r, the federal
    # deduction is r * min(limit, P + S), and the deduction on the principal
    # residence alone is r * min(limit, P).
    draws, values, units, _ = results
    limit = np.array(
        [
            POST_2017_LIMIT.get(status, DEFAULT_POST_2017_LIMIT)
            for status in draws["filing_status"]
        ]
    )
    rate = draws["equal_rate"]
    principal, second = draws["equal_principal"], draws["equal_second"]
    index = units["equal_rate"]
    year_values = values[2026]
    _close(
        year_values["interest_deduction"][index],
        rate * np.minimum(limit, principal + second),
    )
    _close(
        year_values["interest_deduction"][index]
        - year_values["ky_disallowed_second_residence_interest"][index],
        rate * np.minimum(limit, principal),
    )
    # The draws exercise both sides of the limit.
    assert np.any(principal > limit) and np.any(principal + second > limit)
    assert np.any((principal < limit) & (principal + second > limit))


def test_kentucky_follows_the_federal_deduction_before_2026(results):
    _, values, units, _ = results
    before = values[2025]
    _close(
        before["ky_itemized_deductions_unit"][units["base"]]
        - before["ky_itemized_deductions_unit"][units["principal_only"]],
        before["interest_deduction"][units["base"]]
        - before["interest_deduction"][units["principal_only"]],
    )


def test_omitted_and_zero_second_residence_inputs_match(results):
    _, values, units, persons = results
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
            year_values["ky_disallowed_second_residence_interest"][units["omitted"]],
            0,
        )
