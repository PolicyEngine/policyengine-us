from policyengine_us.model_api import *


class md_refundable_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland refundable Child Tax Credit"
    definition_period = YEAR
    unit = USD
    documentation = "Maryland Child Tax Credit"
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-751-effective-until-712026-tax-credit-for-qualified-child"
    defined_for = "md_refundable_ctc_eligible"

    def formula(tax_unit, period, parameters):
        md_ctc = tax_unit("md_ctc", period)
        federal_ctc = tax_unit("ctc", period)
        return max_(md_ctc - federal_ctc, 0)
