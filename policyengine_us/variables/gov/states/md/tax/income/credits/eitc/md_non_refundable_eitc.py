from policyengine_us.model_api import *


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
        federal_eitc = tax_unit("eitc", period)
        md_eitc = parameters(period).gov.states.md.tax.income.credits.eitc
        childless = tax_unit("eitc_child_count", period) == 0
        return where(
            childless,
            min_(md_eitc.childless.max_amount, federal_eitc),
            md_eitc.non_refundable_match * federal_eitc,
        )
