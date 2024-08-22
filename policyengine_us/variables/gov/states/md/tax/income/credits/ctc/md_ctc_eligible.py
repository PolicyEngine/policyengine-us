from policyengine_us.model_api import *


class md_ctc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Maryland Child Tax Credit"
    definition_period = YEAR
    reference = (
        "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-751-effective-until-712026-tax-credit-for-qualified-child"
        "https://law.justia.com/codes/maryland/2022/tax-general/title-10/subtitle-7/section-10-751/"
    )
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.tax.income.credits.ctc
        return tax_unit("adjusted_gross_income", period) <= p.agi_cap
