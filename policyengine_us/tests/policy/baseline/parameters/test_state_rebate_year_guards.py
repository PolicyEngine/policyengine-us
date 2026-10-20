"""Historical rebate guards must preserve the main eligibility-year schedules.

These snapshots come from main at ce9377ee80157a17eb730fa1b8550b4d433c696c.
They compare every amount branch and scale threshold with the fully constructed
model, including parameter backdating. Keeping the baseline here makes the
differential test independent of Git history in shallow CI checkouts.
"""

import pytest

from policyengine_core.parameters import Parameter

from policyengine_us.system import system
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR


def _statuses(single, joint, separate, head_of_household, surviving_spouse):
    return dict(
        zip(
            (
                "SINGLE",
                "JOINT",
                "SEPARATE",
                "HEAD_OF_HOUSEHOLD",
                "SURVIVING_SPOUSE",
            ),
            (single, joint, separate, head_of_household, surviving_spouse),
        )
    )


def _brackets(first_threshold, first_amount, second_threshold, second_amount):
    return {
        "[0].threshold": first_threshold,
        "[0].amount": first_amount,
        "[1].threshold": second_threshold,
        "[1].amount": second_amount,
    }


# Each entry records the first eligibility year followed by main's full dated
# schedule. Repeated eligibility years (MA 2020/2021 and VA 2021/2022/2024) are
# explicit. The later zero/availability dates must also remain unchanged.
MAIN_SCHEDULES = {
    "co.tax.income.credits.sales_tax_refund.in_effect": (
        2021,
        {2021: {"": True}, 2026: {"": False}, 2027: {"": True}},
    ),
    "il.tax.income.credits.income_tax_rebate.amount.joint": (
        2021,
        {2021: _brackets(0, 100, 400_000, 0)},
    ),
    "il.tax.income.credits.income_tax_rebate.amount.other": (
        2021,
        {2021: _brackets(0, 50, 200_000, 0)},
    ),
    "il.tax.income.credits.income_tax_rebate.amount.dependent": (
        2021,
        {2021: {"": 100}},
    ),
    "il.tax.income.credits.property_tax_rebate.cap": (
        2021,
        {2021: {"": 300}},
    ),
    "nm.tax.income.rebates.2021_income.main.amount": (
        2021,
        {2021: _statuses(250, 500, 250, 500, 500)},
    ),
    "nm.tax.income.rebates.2021_income.additional.amount": (
        2021,
        {2021: _statuses(500, 1_000, 500, 1_000, 1_000)},
    ),
    "nm.tax.income.rebates.2021_income.supplemental.amount": (
        2021,
        {2021: _statuses(500, 1_000, 500, 1_000, 1_000)},
    ),
    "va.tax.income.rebate.amount": (
        2021,
        {
            2021: _statuses(250, 500, 250, 250, 250),
            2022: _statuses(200, 400, 200, 200, 200),
            2023: _statuses(0, 0, 0, 0, 0),
            2024: _statuses(200, 400, 200, 200, 200),
            2025: _statuses(0, 0, 0, 0, 0),
        },
    ),
    "hi.tax.income.credits.act_115_rebate.single": (
        2021,
        {2021: _brackets(-float("inf"), 300, 100_000, 100)},
    ),
    "hi.tax.income.credits.act_115_rebate.joint": (
        2021,
        {2021: _brackets(-float("inf"), 300, 200_000, 100)},
    ),
    "ma.tax.income.credits.covid_19_essential_employee_premium_pay_program.amount": (
        2020,
        {2020: {"": 500}, 2021: {"": 500}, 2022: {"": 0}},
    ),
}


def _leaves(path):
    root = system.parameters.get_child(f"gov.states.{path}")
    return {
        parameter.name.removeprefix(root.name).lstrip("."): parameter
        for parameter in (root, *root.get_descendants())
        if isinstance(parameter, Parameter)
    }


@pytest.mark.parametrize("path", MAIN_SCHEDULES)
def test_eligibility_and_later_schedules_equal_main(path):
    first_year, schedule = MAIN_SCHEDULES[path]
    leaves = _leaves(path)
    for year in range(first_year, max(schedule) + 1):
        expected = schedule[max(start for start in schedule if start <= year)]
        actual = {
            name: parameter(f"{year}-01-01") for name, parameter in leaves.items()
        }
        assert actual == expected, (path, year)


@pytest.mark.parametrize(
    "path", [path for path in MAIN_SCHEDULES if not path.startswith("co.")]
)
def test_amounts_zero_in_every_modeled_year_before_eligibility(path):
    first_year, _ = MAIN_SCHEDULES[path]
    # Thresholds must persist so scales remain valid; only amount leaves vanish.
    amounts = {
        name: parameter
        for name, parameter in _leaves(path).items()
        if not name.endswith(".threshold")
    }
    assert amounts
    for year in range(FIRST_MODELED_YEAR, first_year):
        for name, parameter in amounts.items():
            assert parameter(f"{year}-01-01") == 0, (path, name, year)


def test_colorado_historical_availability_preserves_2015():
    in_effect = system.parameters.get_child(
        "gov.states.co.tax.income.credits.sales_tax_refund.in_effect"
    )
    # This asserts availability only: the backdated 2015 amount table is outside
    # the guard fix's scope and is not represented as a verified 2015 schedule.
    assert in_effect("2015-01-01") is True
    for year in range(2016, 2021):
        assert in_effect(f"{year}-01-01") is False
