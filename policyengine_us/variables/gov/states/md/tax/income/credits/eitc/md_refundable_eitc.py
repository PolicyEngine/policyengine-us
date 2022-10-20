from policyengine_us.model_api import *


class md_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD EITC refundable State tax credit"
    unit = USD
    documentation = "Refundable EITC credit reducing MD State income tax."
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        non_refundable_eitc = tax_unit("md_non_refundable_eitc", period)
        md_eitc = parameters(period).gov.states.md.tax.income.credits.eitc
        income_tax = tax_unit("md_income_tax_before_credits", period)
        excess = max_(0, non_refundable_eitc - income_tax)
        childless = tax_unit("eitc_child_count", period) == 0
        return where(
            childless,
            excess,
            md_eitc.refundable_match * excess,
        )
