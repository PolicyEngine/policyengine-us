"""Mississippi and Missouri count the federal miscellaneous deduction once.

Before 2018 the federal miscellaneous deduction above the 2% floor is part of
itemized_taxable_income_deductions and of itemized_deductions_less_salt.
RSMo 143.141 starts Missouri's itemized deduction from the allowable federal
itemized deductions, and Miss. Code Ann. 27-7-17(4) bars deducting the same
item more than once. So for every generated tax unit and year:

1. Holding the federal totals fixed, the miscellaneous deduction does not
   change mo_itemized_deductions or ms_itemized_deductions_unit.
2. Mississippi's total is its non-SALT federal total plus its real estate
   tax deduction.
3. Missouri's total is never negative and never exceeds the federal total
   plus payroll taxes. The worked cases also show it falls with the state
   income tax adjustment.

Property 1 fails whenever the miscellaneous deduction is positive if either
state adds misc_deduction on top of the federal total; the strategy draws it
from $1 to $20,000, never zero, and the years include 2016 and 2017, when
the federal deduction applies.
"""

import hypothesis
import hypothesis.strategies as st
import numpy as np
import pytest

from policyengine_us import Simulation

YEARS = (2016, 2017, 2025)
TOLERANCE = 0.01


def build_situation(cases, state):
    people, tax_units, households = {}, {}, {}
    for i, case in enumerate(cases):
        for with_misc in (True, False):
            key = f"{i}_{int(with_misc)}"
            person = f"person_{key}"
            people[person] = {
                "age": {year: 40 for year in YEARS},
                "employee_social_security_tax": {
                    year: case["payroll_tax"] for year in YEARS
                },
                "employee_medicare_tax": {year: 0 for year in YEARS},
                "self_employment_tax": {year: 0 for year in YEARS},
            }
            misc = case["misc"] if with_misc else 0
            tax_unit = {
                "members": [person],
                "misc_deduction": {year: misc for year in YEARS},
                "additional_medicare_tax": {year: 0 for year in YEARS},
            }
            if state == "MO":
                tax_unit["itemized_taxable_income_deductions"] = {
                    year: case["federal_total"] for year in YEARS
                }
                tax_unit["mo_net_state_income_taxes"] = {
                    year: case["state_tax"] for year in YEARS
                }
            else:
                tax_unit["itemized_deductions_less_salt"] = {
                    year: case["federal_total"] for year in YEARS
                }
                tax_unit["ms_real_estate_tax_deduction"] = {
                    year: case["real_estate"] for year in YEARS
                }
            tax_units[f"tax_unit_{key}"] = tax_unit
            households[f"household_{key}"] = {
                "members": [person],
                "state_code": {year: state for year in YEARS},
            }
    return {"people": people, "tax_units": tax_units, "households": households}


def calculate(cases, state, variable):
    simulation = Simulation(situation=build_situation(cases, state))
    return {
        year: np.asarray(simulation.calculate(variable, year)).reshape(len(cases), 2)
        for year in YEARS
    }


def assert_properties(cases):
    mo = calculate(cases, "MO", "mo_itemized_deductions")
    ms = calculate(cases, "MS", "ms_itemized_deductions_unit")
    for i, case in enumerate(cases):
        for year in YEARS:
            # Column 0 has the miscellaneous deduction, column 1 has none.
            assert mo[year][i, 0] == pytest.approx(mo[year][i, 1], abs=TOLERANCE), (
                case,
                year,
            )
            assert ms[year][i, 0] == pytest.approx(ms[year][i, 1], abs=TOLERANCE), (
                case,
                year,
            )
            assert ms[year][i, 0] == pytest.approx(
                case["federal_total"] + case["real_estate"], abs=TOLERANCE
            ), (case, year)
            assert mo[year][i, 0] >= 0, (case, year)
            assert (
                mo[year][i, 0]
                <= case["federal_total"] + case["payroll_tax"] + TOLERANCE
            ), (case, year)


def test_state_tax_adjustment_does_not_raise_missouri_deduction():
    base = {
        "federal_total": 10_000,
        "misc": 1_000,
        "payroll_tax": 0,
        "real_estate": 2_000,
        "state_tax": 0,
    }
    cases = [base, {**base, "state_tax": 2_000}, {**base, "state_tax": 50_000}]
    mo = calculate(cases, "MO", "mo_itemized_deductions")
    # 10,000 once, less the state income tax adjustment, floored at zero.
    assert mo[2017][:, 0] == pytest.approx([10_000, 8_000, 0], abs=TOLERANCE)
    ms = calculate(cases[:1], "MS", "ms_itemized_deductions_unit")
    # 10,000 once, plus 2,000 real estate taxes.
    assert ms[2017][0, 0] == pytest.approx(12_000, abs=TOLERANCE)
    assert_properties(cases)


AMOUNTS = st.integers(min_value=0, max_value=50_000)


@hypothesis.settings(
    max_examples=10,
    deadline=None,
    derandomize=True,
    suppress_health_check=[hypothesis.HealthCheck.too_slow],
)
@hypothesis.given(
    st.lists(
        st.fixed_dictionaries(
            {
                "federal_total": AMOUNTS,
                "misc": st.integers(min_value=1, max_value=20_000),
                "payroll_tax": st.integers(min_value=0, max_value=10_000),
                "real_estate": AMOUNTS,
                "state_tax": AMOUNTS,
            }
        ),
        min_size=1,
        max_size=8,
    )
)
def test_ms_mo_misc_deduction_counted_once(cases):
    assert_properties(cases)
