from policyengine_us.model_api import *


class md_refundable_ctc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Maryland refundable Child Tax Credit"
    definition_period = YEAR
    documentation = "Maryland Child Tax Credit"
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-751-effective-until-712026-tax-credit-for-qualified-child"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        federal_ctc = tax_unit("ctc", period)
        md_ctc = tax_unit("md_ctc", period)
        return md_ctc > federal_ctc
