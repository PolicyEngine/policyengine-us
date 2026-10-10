from policyengine_us.model_api import *


class ca_claim_of_right_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "California claim of right credit"
    unit = USD
    documentation = (
        "When California tax is computed under the credit method of Cal. Rev. "
        "& Tax. Code 17049, the decrease in the earlier year's California tax "
        "from excluding the repaid income. Any excess over the year's tax is "
        "treated as a payment and refunded (17049(b)). Reported with total "
        "payments on Form 540, line 78."
    )
    definition_period = YEAR
    reference = (
        # Cal. Rev. & Tax. Code 17049, as amended by Stats. 2005, ch. 349 (AB 1767)
        "https://www.leginfo.ca.gov/pub/05-06/bill/asm/ab_1751-1800/ab_1767_bill_20050922_chaptered.html",
        # 2025 Form 540 booklet, line 78
        "https://www.ftb.ca.gov/forms/2025/2025-540-booklet.pdf#page=17",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("ca_claim_of_right_eligible", period)
        credit_applies = tax_unit("ca_claim_of_right_credit_applies", period)
        person = tax_unit.members
        decrease = person("ca_claim_of_right_prior_year_tax_decrease", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        prior_year_tax_decrease = tax_unit.sum(decrease * head_or_spouse)
        return where(eligible & credit_applies, prior_year_tax_decrease, 0)
