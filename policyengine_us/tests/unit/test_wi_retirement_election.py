"""Check accounting and reporting invariants beyond individual YAML amounts.

One shared vectorized simulation and two scalar controls verify independence
between returns. YAML cases cannot compare vectorized and separate executions
or express equality between alternative reporting routes across input rows.
"""

import numpy as np
import pytest

from policyengine_us import Simulation


def _situation(cases, year):
    situation = {
        entity: {}
        for entity in (
            "people",
            "tax_units",
            "spm_units",
            "families",
            "marital_units",
            "households",
        )
    }
    for index, case in enumerate(cases):
        members = []
        for person_index, person in enumerate(case["people"]):
            name = f"person_{index}_{person_index}"
            members.append(name)
            situation["people"][name] = {
                variable: {str(year): value}
                for variable, value in {
                    **person,
                    "is_tax_unit_head": person_index == 0,
                    "is_tax_unit_spouse": person_index == 1,
                }.items()
            }
        unit_name = f"unit_{index}"
        for entity in ("spm_units", "families", "marital_units"):
            situation[entity][unit_name] = {"members": members}
        situation["tax_units"][unit_name] = {
            "members": members,
            "filing_status": {str(year): "JOINT" if len(members) == 2 else "SINGLE"},
            **{
                variable: {str(year): value}
                for variable, value in case.get("tax", {}).items()
            },
        }
        situation["households"][unit_name] = {
            "members": members,
            "state_code": {str(year): "WI"},
        }
    return situation


RETIREMENT_CASES = [
    {"people": [{"age": 68, "taxable_private_pension_income": 8_000}]},
    {"people": [{"age": 68, "taxable_private_pension_income": 30_000}]},
    {"people": [{"age": 66, "taxable_private_pension_income": 30_000}]},
    {
        "people": [
            {
                "age": 68,
                "taxable_private_pension_income": 45_000,
                "farm_operations_income": -30_000,
            },
            {"age": 68, "taxable_private_pension_income": 8_000},
        ]
    },
    {
        "people": [
            {
                "age": 68,
                "taxable_private_pension_income": 53_000,
                "farm_operations_income": -35_000,
            },
            {"age": 68, "taxable_private_pension_income": 5_000},
        ]
    },
    {
        "people": [
            {"age": 68, "taxable_private_pension_income": 8_000},
            {"age": 66, "taxable_private_pension_income": 8_000},
        ]
    },
    {
        "people": [{"age": 68, "taxable_private_pension_income": 30_000}],
        "tax": {
            "wi_income_tax_before_credits": 1_000,
            "wi_non_refundable_credits": 100,
            "wi_retirement_income_exclusion_tax": 100,
            "wi_earned_income_credit": 25,
            "wi_homestead_credit": 200,
        },
    },
    {"people": [{"age": 68, "taxable_ira_distributions": 8_000}]},
    {"people": [{"age": 68, "taxable_401k_distributions": 8_000}]},
    {"people": [{"age": 68, "taxable_roth_conversions": 8_000}]},
]


CAPITAL_AMOUNTS = [
    (0, 1_000, 0),
    (0, 1_000, -800),
    (0, 1_000, -1_200),
    (2_000, 1_000, -800),
    (-1_000, 1_500, -800),
    (-2_000, 1_000, 3_000),
]


def _capital_gain_cases():
    direct_cases = []
    schedule_d_cases = []
    for long_term, distribution, short_term in CAPITAL_AMOUNTS:
        common = {
            "age": 40,
            "employment_income": 40_000,
            "short_term_capital_gains": short_term,
        }
        direct_cases.append(
            {
                "people": [
                    {
                        **common,
                        "long_term_capital_gains": long_term,
                        "non_sch_d_capital_gains": distribution,
                    }
                ]
            }
        )
        schedule_d_cases.append(
            {
                "people": [
                    {
                        **common,
                        "long_term_capital_gains": long_term + distribution,
                    }
                ]
            }
        )
    return direct_cases, schedule_d_cases


@pytest.fixture(scope="module")
def wi_simulation():
    direct_cases, schedule_d_cases = _capital_gain_cases()
    return Simulation(
        situation=_situation(RETIREMENT_CASES + direct_cases + schedule_d_cases, 2026)
    )


def test_retirement_election_vectorized_matches_separate_returns(wi_simulation):
    simulation = wi_simulation
    year = 2026
    retirement_slice = slice(0, len(RETIREMENT_CASES))
    variables = (
        "wi_retirement_income_exclusion_amount",
        "wi_retirement_income_exclusion_line17_offset",
        "wi_retirement_income_exclusion_tax",
        "wi_retirement_income_exclusion_elected",
        "state_income_tax_before_refundable_credits",
        "state_refundable_credits",
        "state_income_tax",
    )
    vectorized = {
        variable: simulation.calculate(variable, year)[retirement_slice]
        for variable in variables
    }
    # Compare an unequal-pension joint return and a return retaining homestead.
    # The remaining rows exercise their vectorized accounting identities below.
    for index in (4, 6):
        case = RETIREMENT_CASES[index]
        separate = Simulation(situation=_situation([case], year))
        for variable in variables:
            assert vectorized[variable][index] == pytest.approx(
                separate.calculate(variable, year)[0], abs=0.01
            )

    before = vectorized["state_income_tax_before_refundable_credits"]
    refundable = vectorized["state_refundable_credits"]
    net = vectorized["state_income_tax"]
    elected = vectorized["wi_retirement_income_exclusion_elected"]
    standard_before = np.maximum(
        0,
        simulation.calculate("wi_income_tax_before_credits", year)
        - simulation.calculate("wi_non_refundable_credits", year),
    )[retirement_slice]
    earned_income_credit = simulation.calculate("wi_earned_income_credit", year)[
        retirement_slice
    ]
    homestead_credit = simulation.calculate("wi_homestead_credit", year)[
        retirement_slice
    ]
    standard_net = standard_before - earned_income_credit - homestead_credit

    np.testing.assert_allclose(net, before - refundable, atol=0.01)
    assert np.all(net <= standard_net + 0.01)
    assert np.any(elected)
    assert np.any(~elected)
    np.testing.assert_allclose(
        refundable[elected], homestead_credit[elected], atol=0.01
    )
    np.testing.assert_allclose(
        before[elected],
        vectorized["wi_retirement_income_exclusion_tax"][elected],
        atol=0.01,
    )
    np.testing.assert_allclose(before[~elected], standard_before[~elected], atol=0.01)

    offset = vectorized["wi_retirement_income_exclusion_line17_offset"]
    line17 = simulation.calculate("wi_retirement_income_subtraction", year)[
        retirement_slice
    ]
    assert np.all(offset >= 0)
    assert np.all(offset <= line17)
    assert np.all(offset <= vectorized["wi_retirement_income_exclusion_amount"])


def test_capital_gain_distribution_reporting_route_and_loss_bounds(wi_simulation):
    count = len(CAPITAL_AMOUNTS)
    start = len(RETIREMENT_CASES)
    direct_slice = slice(start, start + count)
    schedule_d_slice = slice(start + count, start + 2 * count)
    subtraction = wi_simulation.calculate("wi_capital_gain_loss_subtraction", 2026)
    np.testing.assert_allclose(
        subtraction[direct_slice], subtraction[schedule_d_slice], atol=0.01
    )

    # Compare downstream tax when the original Schedule D has no net loss;
    # federal and Wisconsin loss-addition conventions are outside this fix.
    nonloss_rows = [0, 3, 5]
    for variable in (
        "wi_agi",
        "state_income_tax_before_refundable_credits",
        "state_income_tax",
    ):
        values = wi_simulation.calculate(variable, 2026)
        np.testing.assert_allclose(
            values[direct_slice][nonloss_rows],
            values[schedule_d_slice][nonloss_rows],
            atol=0.01,
        )

    subtraction = subtraction[direct_slice]
    long_term = np.array(
        [gain + distribution for gain, distribution, _ in CAPITAL_AMOUNTS]
    )
    net_gain = long_term + np.array(
        [short_term for _, _, short_term in CAPITAL_AMOUNTS]
    )
    assert np.all(subtraction >= 0)
    assert np.all(subtraction <= 0.3 * np.maximum(long_term, 0) + 0.01)
    assert np.all(subtraction <= 0.3 * np.maximum(net_gain, 0) + 0.01)
    np.testing.assert_array_equal(subtraction[net_gain <= 0], 0)
