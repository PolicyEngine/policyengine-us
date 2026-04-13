from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ga_itemizer_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia itemizer tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/georgia/2022/title-48/chapter-7/article-2/section-48-7-29-23/"
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
            "ga_itemizer_credit",
            "ga_itemizer_credit_potential",
        )
