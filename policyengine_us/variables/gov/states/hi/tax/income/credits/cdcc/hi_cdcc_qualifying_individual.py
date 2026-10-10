from policyengine_us.model_api import *


class hi_cdcc_qualifying_individual(Variable):
    value_type = bool
    entity = Person
    label = "Qualifying individual for the Hawaii child and dependent care credit"
    defined_for = StateCode.HI
    definition_period = YEAR
    # PDF pages 46-47: HRS 235-55.6(a)(1) and (b)(1).
    reference = "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=46"

    def formula(person, period, parameters):
        # HRS 235-55.6(b)(1): (A) "A dependent of the taxpayer who is under
        # the age of thirteen", (B) "A dependent of the taxpayer who is
        # physically or mentally incapable of caring for oneself", or (C) the
        # incapacitated spouse. Unlike IRC 21(b)(1)(B), (B) does not disregard
        # IRC 152(b)(1), so a return on which a filer can be claimed as a
        # dependent has no dependent qualifying individual.
        federal = person("is_cdcc_eligible", period)
        filer = person("is_tax_unit_head_or_spouse", period)
        claimed = person("claimed_as_dependent_on_another_return", period)
        dependent_filer = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        # HRS 235-55.6(a)(1) allows the credit to a taxpayer who "is not
        # claimed or is not otherwise eligible to be claimed as a dependent",
        # so an incapacitated filer is the qualifying individual only of a
        # spouse who cannot be claimed.
        claimed_filers = person.tax_unit.sum(filer & claimed)
        other_filer_claimed = (claimed_filers - (filer & claimed)) > 0
        spouse_route = federal & filer & ~other_filer_claimed
        return where(dependent_filer, spouse_route, federal)
