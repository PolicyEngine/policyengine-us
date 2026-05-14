from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    ordered_capped_state_non_refundable_credits,
)


class ma_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA non-refundable credits"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/doc/2021-form-1-massachusetts-resident-income-tax-return/download"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ma.tax.income.credits.non_refundable
        return ordered_capped_state_non_refundable_credits(
            tax_unit, period, ordered_credits, "ma_income_tax_before_credits"
        )
