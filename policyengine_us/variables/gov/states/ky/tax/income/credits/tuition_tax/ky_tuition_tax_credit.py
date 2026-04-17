from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ky_tuition_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky tuition tax credit"  # Form 8863-K
    unit = USD
    definition_period = YEAR
    defined_for = "ky_tuition_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ky.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "ky_income_tax_before_non_refundable_credits_unit",
            "ky_tuition_tax_credit",
            "ky_tuition_tax_credit_potential",
        )
