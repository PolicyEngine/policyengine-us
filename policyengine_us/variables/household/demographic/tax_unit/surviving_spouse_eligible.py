from policyengine_us.model_api import *


class surviving_spouse_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Qualifies for surviving spouse filing status"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/2#a",
        # Publication 501, eligibility rule 3: the child counts if you "could
        # claim as a dependent except that ... You could be claimed as a
        # dependent on someone else's return."
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=11",
    )

    def formula(tax_unit, period, parameters):
        # The surviving spouse filing status should only apply to surviving spouse heads
        # who maintain a household for at least one dependent.
        # IRC 2(a)(1)(B)(i) determines that dependency "without regard to
        # subsections (b)(1), (b)(2), and (d)(1)(B)" of section 152, so a
        # surviving spouse who can be claimed as a dependent on another
        # return still qualifies. The child count is therefore not gated on
        # head_or_spouse_is_dependent_elsewhere.
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        is_surviving_spouse = person("is_surviving_spouse", period)
        surviving_spouse_head = tax_unit.any(is_head & is_surviving_spouse)
        has_child_dependents = tax_unit("tax_unit_child_dependents", period) > 0
        married = tax_unit("tax_unit_married", period)
        return surviving_spouse_head & has_child_dependents & ~married
