from policyengine_us.model_api import *


class ct_claim_of_right_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut claim of right credit"
    unit = USD
    documentation = (
        "When a filer repays income that was included in Connecticut "
        "adjusted gross income in an earlier year under a claim of right and "
        "determines federal tax under 26 U.S.C. 1341(a)(4) or (5), "
        "Connecticut tax is reduced by the decrease in the earlier year's "
        "Connecticut tax from excluding the repaid income (Conn. Gen. Stat. "
        "12-711a(a)(1)). The credit applies under either federal method, "
        "unless the repayment is deducted in arriving at federal adjusted "
        "gross income, which claim_of_right_repayment excludes. Any excess "
        "over the year's tax is refunded (12-711a(a)(3)). Reported on Form "
        "CT-1040, line 20b, from Form CT-1040 CRC, line 6."
    )
    definition_period = YEAR
    reference = (
        "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-711a",
        # 2025 Form CT-1040 CRC
        "https://portal.ct.gov/-/media/drs/forms/2025/income/ct-1040-crc_1225.pdf#page=1",
    )
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        # Section 1341 governs federal tax, under paragraph (a)(4) or (a)(5),
        # when the repayment exceeds the federal threshold.
        eligible = tax_unit("claim_of_right_section_1341_eligible", period)
        prior_year_tax_decrease = tax_unit(
            "ct_claim_of_right_prior_year_tax_decrease", period
        )
        return where(eligible, prior_year_tax_decrease, 0)
