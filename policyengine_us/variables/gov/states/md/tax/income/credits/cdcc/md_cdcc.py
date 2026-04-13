from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class md_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD CDCC"
    documentation = "Maryland Child and Dependent Care Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-716-for-child-care-or-dependent-care"
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
            "md_cdcc",
            "md_cdcc_potential",
        )
