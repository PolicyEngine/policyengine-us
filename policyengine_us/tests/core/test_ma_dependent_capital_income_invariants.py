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


def build_situation(units, year=YEAR):
    people, tax_units, marital_units, households = {}, {}, {}, {}
    for index, unit in enumerate(units):
        members = []
        filer_count = len(unit["filers"])
        for member_index, inputs in enumerate(unit["filers"] + unit["dependents"]):
            name = f"person_{index}_{member_index}"
            is_filer = member_index < filer_count
            people[name] = {
                "age": {year: 40 if is_filer else 10},
                "is_tax_unit_head": {year: member_index == 0},
                "is_tax_unit_spouse": {year: is_filer and member_index == 1},
                "is_tax_unit_dependent": {year: not is_filer},
                **{variable: {year: value} for variable, value in inputs.items()},
            }
            members.append(name)
            if not is_filer:
                marital_units[f"dependent_{index}_{member_index}"] = {"members": [name]}
        tax_units[f"tax_unit_{index}"] = {"members": members}
        marital_units[f"filers_{index}"] = {"members": members[:filer_count]}
        households[f"household_{index}"] = {
            "members": members,
            "state_code": {year: "MA"},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "households": households,
    }


def check_twins(units, year=YEAR, outputs=INVARIANT_OUTPUTS):
    twins = [without_dependent_income(unit) for unit in units]
    simulation = Simulation(situation=build_situation(units + twins, year))
    unit_count = len(units)
    results = {}
    for variable in outputs:
        values = np.asarray(simulation.calculate(variable, year))
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


@settings(max_examples=3, deadline=None, derandomize=True)
@given(
    st.lists(
        st.tuples(
            st.integers(5_000, 20_000),
            st.integers(1_000, 10_000),
            st.integers(5_000, 100_000),
            st.integers(0, 100_000),
        ),
        min_size=4,
        max_size=8,
    )
)
def test_2021_unemployment_worksheet_ignores_dependent_income(amounts):
    units = [
        {
            "filers": [
                {
                    "employment_income": wages,
                    "unemployment_compensation": unemployment,
                }
            ],
            "dependents": [
                {
                    "tax_exempt_interest_income": interest,
                    "social_security_survivors": social_security,
                }
            ],
        }
        for wages, unemployment, interest, social_security in amounts
    ]
    zero_income_twins = [
        {
            **unit,
            "dependents": [
                {
                    "tax_exempt_interest_income": 0,
                    "social_security_survivors": 0,
                }
            ],
        }
        for unit in units
    ]
    simulation = Simulation(situation=build_situation(units + zero_income_twins, 2021))
    values = simulation.calculate("ma_qualified_unemployment_deduction", 2021)
    # Filer income stays below 34,480 and unemployment stays below 10,200.
    expected = [unemployment for _, unemployment, _, _ in amounts]
    np.testing.assert_allclose(values, expected + expected, rtol=0, atol=0.01)
