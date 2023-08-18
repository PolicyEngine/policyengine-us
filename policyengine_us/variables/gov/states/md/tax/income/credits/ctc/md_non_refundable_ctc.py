from policyengine_us.model_api import *


class md_non_refundable_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland non-refundable Child Tax Credit"
    definition_period = YEAR
    unit = USD
    documentation = "Maryland Child Tax Credit"
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-751-effective-until-712026-tax-credit-for-qualified-child"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        if parameters(
            period
        ).gov.states.md.tax.income.credits.ctc.non_refundable_eligible:
            md_ctc = tax_unit("md_ctc", period)
            federal_ctc = tax_unit("ctc", period)
            return min_(md_ctc, federal_ctc)
        return 0
