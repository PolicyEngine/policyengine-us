from policyengine_us.model_api import *


class ca_claim_of_right_prior_year_tax_decrease(Variable):
    value_type = float
    entity = Person
    label = (
        "California prior-year tax decrease from excluding repaid claim of right income"
    )
    unit = USD
    documentation = (
        "Decrease in California income tax for the earlier year or years that "
        "would result solely from excluding the amount repaid this year "
        "(claim_of_right_repayment) from the gross income required to be "
        "shown on the California return for that year. The tax unit uses the "
        "sum for its head and spouse."
    )
    definition_period = YEAR
    reference = (
        # Cal. Rev. & Tax. Code 17049, as amended by Stats. 2005, ch. 349 (AB 1767)
        "https://www.leginfo.ca.gov/pub/05-06/bill/asm/ab_1751-1800/ab_1767_bill_20050922_chaptered.html",
        # 2025 FTB Publication 1001, Claim of right
        "https://www.ftb.ca.gov/forms/2025/2025-1001-publication.pdf#page=25",
        # 2025 Form 540 booklet, Schedule CA (540) Part II line 16
        "https://www.ftb.ca.gov/forms/2025/2025-540-booklet.pdf#page=67",
    )
    defined_for = StateCode.CA
