from policyengine_us.model_api import *


class md_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland Child Tax Credit"
    definition_period = YEAR
    unit = USD
    reference = (
        "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-751-effective-until-712026-tax-credit-for-qualified-child"
        "https://law.justia.com/codes/maryland/2022/tax-general/title-10/subtitle-7/section-10-751/"
    )
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        ctc_2021 = tax_unit("md_ctc_2021", period)
        ctc_2023 = tax_unit("md_ctc_2023", period)
        return where(period.start.year >= 2023, ctc_2023, ctc_2021)
