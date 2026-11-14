"""Keep dependents' capital income off the filers' Massachusetts return.

Massachusetts Schedule D takes gains and distributions from the filers'
federal return. The Commonwealth excludes children's income from their
parents' income:
https://budget.digital.mass.gov/govbudget/fy27/tax-expenditure-budget/personal-income-tax/introduction/

Compare each tax unit with a twin whose dependents have no capital income.
Filer wages start at $80,000 to avoid earned income tax credit interactions.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2025
CAPITAL_INPUTS = [
    "short_term_capital_gains",
    "long_term_capital_gains",
    "non_sch_d_capital_gains",
    "qualified_dividend_income",
    "non_qualified_dividend_income",
]
INVARIANT_OUTPUTS = [
    "ma_income_tax",
    "ma_part_a_agi",
    "ma_part_c_agi",
    "ma_long_term_capital_gains",
    "ma_short_term_loss_against_dividends",
    "ma_long_term_loss_against_dividends",
    "ma_part_a_adjusted_dividends",
]


def without_dependent_income(unit):
    zero = {name: 0.0 for name in CAPITAL_INPUTS}
    return {
        **unit,
        "dependents": [{**dependent, **zero} for dependent in unit["dependents"]],
    }


def build_situation(units):
    people, tax_units, marital_units, households = {}, {}, {}, {}
    for index, unit in enumerate(units):
        members = []
        filer_count = len(unit["filers"])
        for member_index, inputs in enumerate(unit["filers"] + unit["dependents"]):
            name = f"person_{index}_{member_index}"
            is_filer = member_index < filer_count
            people[name] = {
                "age": {YEAR: 40 if is_filer else 10},
                "is_tax_unit_head": {YEAR: member_index == 0},
                "is_tax_unit_spouse": {YEAR: is_filer and member_index == 1},
                "is_tax_unit_dependent": {YEAR: not is_filer},
                **{variable: {YEAR: value} for variable, value in inputs.items()},
            }
            members.append(name)
            if not is_filer:
                marital_units[f"dependent_{index}_{member_index}"] = {"members": [name]}
        tax_units[f"tax_unit_{index}"] = {"members": members}
        marital_units[f"filers_{index}"] = {"members": members[:filer_count]}
        households[f"household_{index}"] = {
            "members": members,
            "state_code": {YEAR: "MA"},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "households": households,
    }


def check_twins(units):
    twins = [without_dependent_income(unit) for unit in units]
    simulation = Simulation(situation=build_situation(units + twins))
    unit_count = len(units)
    results = {}
    for variable in INVARIANT_OUTPUTS:
        values = np.asarray(simulation.calculate(variable, YEAR))
        np.testing.assert_allclose(
            values[:unit_count],
            values[unit_count:],
            rtol=0,
            atol=0.01,
            err_msg=variable,
        )
        results[variable] = values[:unit_count]
    return results


def test_dependent_losses_and_dividends_do_not_change_filer_loss_offsets():
    units = [
        {
            "filers": [
                {
                    "employment_income": 80_000,
                    "non_qualified_dividend_income": 1_000,
                }
            ],
            "dependents": [{"short_term_capital_gains": -3_000}],
        },
        {
            "filers": [
                {
                    "employment_income": 80_000,
                    "short_term_capital_gains": -1_000,
                    "long_term_capital_gains": 5_000,
                }
            ],
            "dependents": [{"non_qualified_dividend_income": 5_000}],
        },
        {
            "filers": [
                {
                    "employment_income": 80_000,
                    "long_term_capital_gains": -1_000,
                    "non_qualified_dividend_income": 3_000,
                }
            ],
            "dependents": [{"short_term_capital_gains": 5_000}],
        },
        {
            "filers": [
                {
                    "employment_income": 80_000,
                    "short_term_capital_gains": 2_000,
                    "non_qualified_dividend_income": 1_000,
                }
            ],
            "dependents": [{"long_term_capital_gains": -5_000}],
        },
        {
            "filers": [
                {
                    "employment_income": 80_000,
                    "long_term_capital_gains": 1_000,
                }
            ],
            "dependents": [{"non_sch_d_capital_gains": 2_000}],
        },
    ]
    results = check_twins(units)
    # Only the filer's losses offset the filer's dividends and gains.
    # The second filer applies 1,000 of short-term loss against 5,000 of gain.
    # The third filer applies 1,000 of long-term loss against 3,000 of dividends.
    expected = {
        "ma_short_term_loss_against_dividends": [0, 0, 0, 0, 0],
        "ma_long_term_loss_against_dividends": [0, 0, 1_000, 0, 0],
        "ma_part_a_adjusted_dividends": [1_000, 0, 2_000, 1_000, 0],
        "ma_part_a_agi": [1_000, 0, 2_000, 3_000, 0],
        "ma_part_c_agi": [0, 4_000, 0, 0, 1_000],
    }
    for variable, values in expected.items():
        np.testing.assert_allclose(
            results[variable], values, rtol=0, atol=0.01, err_msg=variable
        )


capital_income = st.fixed_dictionaries(
    {
        "short_term_capital_gains": st.integers(-20_000, 20_000),
        "long_term_capital_gains": st.integers(-20_000, 20_000),
        "non_sch_d_capital_gains": st.integers(0, 20_000),
        "qualified_dividend_income": st.integers(0, 20_000),
        "non_qualified_dividend_income": st.integers(0, 20_000),
    }
)


@st.composite
def tax_unit_inputs(draw):
    filers = [
        {
            **draw(capital_income),
            "employment_income": draw(st.integers(80_000, 200_000)),
        }
    ]
    if draw(st.booleans()):
        filers.append(
            {
                **draw(capital_income),
                "employment_income": draw(st.integers(0, 60_000)),
            }
        )
    dependents = draw(st.lists(capital_income, min_size=1, max_size=2))
    return {"filers": filers, "dependents": dependents}


@settings(
    max_examples=3,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(tax_unit_inputs(), min_size=4, max_size=8))
def test_ma_tax_and_capital_income_ignore_dependents_own_amounts(units):
    check_twins(units)
