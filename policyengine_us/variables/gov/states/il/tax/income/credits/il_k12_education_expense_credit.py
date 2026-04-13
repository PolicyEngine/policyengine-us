from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class il_k12_education_expense_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois K-12 Education Expense Credit"
    unit = USD
    definition_period = YEAR

    defined_for = "il_is_exemption_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.credits.k12
        tuition_and_fees = tax_unit("k12_tuition_and_fees", period)
        reduced_tuition_and_fees = max_(0, tuition_and_fees - p.reduction)
        return min_(reduced_tuition_and_fees * p.rate, p.cap)


class il_k12_education_expense_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois K-12 Education Expense Credit"
    unit = USD
    definition_period = YEAR

    defined_for = "il_is_exemption_eligible"

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.il.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "il_income_tax_before_non_refundable_credits",
            "il_k12_education_expense_credit",
            "il_k12_education_expense_credit_potential",
        )
