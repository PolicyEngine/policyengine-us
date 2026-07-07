from policyengine_us.model_api import *


class vt_low_income_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont low-income child care and dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2021.pdf#page=2"
        "https://law.justia.com/codes/vermont/2021/title-32/chapter-151/section-5828c/"
    )
    defined_for = "vt_low_income_cdcc_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.credits.cdcc.low_income
        # 32 V.S.A. § 5824 adopts the federal income tax laws as in effect on
        # December 31, 2024, so from 2026 Vermont uses the pre-OBBBA federal
        # credit (excluding the OBBBA section 21 rate increase).
        if period.start.year >= 2026:
            federal_cdcc = tax_unit("pre_obbba_capped_cdcc", period)
        else:
            federal_cdcc = tax_unit("capped_cdcc", period)
        return p.rate * federal_cdcc
