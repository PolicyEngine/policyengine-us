import policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap as credit_cap_module
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
    cap_state_non_refundable_credit,
    ordered_capped_state_non_refundable_credits,
    state_non_refundable_credit_limit,
)


class FakeTaxUnit:
    def __init__(self, values):
        self.values = values

    def __call__(self, variable, period):
        return self.values[variable]


def test_state_non_refundable_credit_limit_only_counts_preceding_credits(
    monkeypatch,
):
    monkeypatch.setattr(
        credit_cap_module,
        "add",
        lambda tax_unit, period, variables: sum(
            tax_unit(variable, period) for variable in variables
        ),
    )
    tax_unit = FakeTaxUnit(
        {
            "income_tax_before_credits": 50,
            "first_credit": 20,
            "target_credit": 40,
            "later_credit": 999,
        }
    )

    limit = state_non_refundable_credit_limit(
        tax_unit=tax_unit,
        period=2024,
        ordered_credits=["first_credit", "target_credit", "later_credit"],
        income_tax_before_non_refundable_credits_var="income_tax_before_credits",
        credit_name="target_credit",
    )

    assert limit == 30


def test_applied_state_non_refundable_credit_caps_to_remaining_liability(
    monkeypatch,
):
    monkeypatch.setattr(
        credit_cap_module,
        "add",
        lambda tax_unit, period, variables: sum(
            tax_unit(variable, period) for variable in variables
        ),
    )
    tax_unit = FakeTaxUnit(
        {
            "income_tax_before_credits": 50,
            "first_credit": 20,
            "target_credit_potential": 40,
        }
    )

    applied = applied_state_non_refundable_credit(
        tax_unit=tax_unit,
        period=2024,
        ordered_credits=["first_credit", "target_credit"],
        income_tax_before_non_refundable_credits_var="income_tax_before_credits",
        credit_name="target_credit",
        potential_credit_name="target_credit_potential",
    )

    assert applied == 30


def test_cap_state_non_refundable_credit_keeps_raw_variable_as_potential():
    assert (
        cap_state_non_refundable_credit(
            tax_unit=None,
            period=2024,
            credit_name="target_credit",
            ordered_credits=["first_credit", "target_credit"],
            income_tax_before_non_refundable_credits_var="income_tax_before_credits",
            potential=123,
        )
        == 123
    )


def test_ordered_capped_state_non_refundable_credits_never_exceed_tax():
    tax_unit = FakeTaxUnit(
        {
            "income_tax_before_credits": 50,
            "first_credit": 40,
            "second_credit": 40,
            "third_credit": 10,
        }
    )

    capped_total = ordered_capped_state_non_refundable_credits(
        tax_unit=tax_unit,
        period=2024,
        ordered_credits=["first_credit", "second_credit", "third_credit"],
        income_tax_before_non_refundable_credits_var="income_tax_before_credits",
    )

    assert capped_total == 50
