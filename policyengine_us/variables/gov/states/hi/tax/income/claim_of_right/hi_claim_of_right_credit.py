from policyengine_us.model_api import *


class hi_claim_of_right_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii claim of right tax credit"
    unit = USD
    documentation = (
        "When Hawaii tax is computed under section 1341(a)(5), the decrease "
        "in prior-year Hawaii tax from excluding the repaid income (Form "
        "N-364, line 6). It is a refundable credit (Schedule CR, line 9)."
    )
    definition_period = YEAR
    reference = (
        "https://files.hawaii.gov/tax/forms/2025/n364_i.pdf",
        # 2025 Schedule CR, Part I, line 9
        "https://files.hawaii.gov/tax/forms/2025/schcr_i.pdf",
    )
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("hi_claim_of_right_section_1341_eligible", period)
        credit_applies = tax_unit("hi_claim_of_right_credit_applies", period)
        decrease = tax_unit("hi_claim_of_right_prior_year_tax_decrease", period)
        return where(eligible & credit_applies, decrease, 0)
