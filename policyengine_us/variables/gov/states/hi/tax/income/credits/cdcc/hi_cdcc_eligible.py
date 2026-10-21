from policyengine_us.model_api import *


class hi_cdcc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Hawaii child and dependent care credit eligible"
    defined_for = StateCode.HI
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/hawaii/title-14/chapter-235/section-235-55-6/",
        # PDF pages 46-47
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=46",
    )

    def formula(tax_unit, period, parameters):
        # HRS §235-55.6(a)(1) allows the credit to a taxpayer who "is not
        # claimed or is not otherwise eligible to be claimed as a dependent".
        # On a joint return a spouse who cannot be claimed may claim it for
        # an incapacitated spouse who can be claimed.
        has_qualifying_individual = (
            tax_unit("hi_cdcc_qualifying_individuals", period) > 0
        )
        every_filer_dependent = tax_unit("every_filer_is_dependent_elsewhere", period)
        # HRS §235-55.6(e)(2): a married taxpayer may claim the credit only
        # on a joint return, unless (e)(4) treats them as unmarried — the
        # same special rules as IRC §21(e)(2) and (4).
        filing_status_eligible = tax_unit("cdcc_filing_status_eligible", period)
        return (
            has_qualifying_individual & filing_status_eligible & ~every_filer_dependent
        )
