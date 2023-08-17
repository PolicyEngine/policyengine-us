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

    adds = ["md_ctc"]
