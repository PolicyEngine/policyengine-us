from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class md_non_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD EITC non-refundable State tax credit"
    unit = USD
    documentation = "Non-refundable EITC credit reducing MD State income tax."
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income"
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
            "md_non_refundable_eitc",
            "md_non_refundable_eitc_potential",
        )
