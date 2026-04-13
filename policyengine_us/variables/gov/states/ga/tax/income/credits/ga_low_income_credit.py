from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ga_low_income_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia low income credit"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download"
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ga.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "ga_income_tax_before_non_refundable_credits",
            "ga_low_income_credit",
            "ga_low_income_credit_potential",
        )
