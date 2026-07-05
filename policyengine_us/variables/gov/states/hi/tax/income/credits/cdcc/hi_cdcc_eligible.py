from policyengine_us.model_api import *


class hi_cdcc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Hawaii child and dependent care credit eligible"
    defined_for = StateCode.HI
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/hawaii/title-14/chapter-235/section-235-55-6/",
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=47",
    )

    def formula(tax_unit, period, parameters):
        count_cdcc_eligible = tax_unit("count_cdcc_eligible", period)
        # HRS §235-55.6(e)(2): a married taxpayer may claim the credit only
        # on a joint return, unless (e)(4) treats them as unmarried — the
        # same special rules as IRC §21(e)(2) and (4).
        filing_status_eligible = tax_unit("cdcc_filing_status_eligible", period)
        return (count_cdcc_eligible > 0) & filing_status_eligible
