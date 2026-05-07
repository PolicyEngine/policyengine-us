from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class md_poverty_line_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Poverty Line Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/maryland/2021/tax-general/title-10/subtitle-7/section-10-709/"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.md.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "md_income_tax_before_credits",
            "md_poverty_line_credit",
            "md_poverty_line_credit_potential",
        )
