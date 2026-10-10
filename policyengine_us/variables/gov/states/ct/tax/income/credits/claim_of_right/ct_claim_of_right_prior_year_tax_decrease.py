from policyengine_us.model_api import *


class ct_claim_of_right_prior_year_tax_decrease(Variable):
    value_type = float
    entity = Person
    label = (
        "Connecticut prior-year tax decrease from excluding repaid claim of "
        "right income"
    )
    unit = USD
    documentation = (
        "Decrease in Connecticut income tax for the earlier year or years "
        "that would result solely from excluding from Connecticut adjusted "
        "gross income the amount repaid this year "
        "(claim_of_right_repayment): the tax liability reported for the year "
        "of receipt less that liability after excluding the repaid income "
        "(Form CT-1040 CRC, lines 4 to 6). The tax unit uses the sum for its "
        "head and spouse."
    )
    definition_period = YEAR
    reference = (
        "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-711a",
        # 2025 Form CT-1040 CRC, lines 4 to 6
        "https://portal.ct.gov/-/media/drs/forms/2025/income/ct-1040-crc_1225.pdf#page=1",
    )
    defined_for = StateCode.CT
