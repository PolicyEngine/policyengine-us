from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class az_charitable_contributions_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona charitable contributions credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = "https://law.justia.com/codes/arizona/2022/title-43/section-43-1088/"

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.az.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "az_income_tax_before_non_refundable_credits",
            "az_charitable_contributions_credit",
            "az_charitable_contributions_credit_potential",
        )
