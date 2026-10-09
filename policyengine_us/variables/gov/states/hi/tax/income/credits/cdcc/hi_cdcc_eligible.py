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
        # HRS §235-55.6(a)(1) allows the credit to a taxpayer who "is not
        # claimed or is not otherwise eligible to be claimed as a dependent".
        # On a joint return a spouse who cannot be claimed may claim it for
        # the qualifying individuals, including an incapacitated spouse who
        # can be claimed; an incapacitated filer is not the qualifying
        # individual of a spouse who can be claimed.
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        claimed = person("claimed_as_dependent_on_another_return", period)
        claimed_filers = tax_unit.sum(filer & claimed)
        other_filer_claimed = (claimed_filers - (filer & claimed)) > 0
        recipient = person("is_cdcc_eligible", period) & ~(filer & other_filer_claimed)
        every_filer_dependent = tax_unit("every_filer_is_dependent_elsewhere", period)
        # HRS §235-55.6(e)(2): a married taxpayer may claim the credit only
        # on a joint return, unless (e)(4) treats them as unmarried — the
        # same special rules as IRC §21(e)(2) and (4).
        filing_status_eligible = tax_unit("cdcc_filing_status_eligible", period)
        return (
            (tax_unit.sum(recipient) > 0)
            & filing_status_eligible
            & ~every_filer_dependent
        )
