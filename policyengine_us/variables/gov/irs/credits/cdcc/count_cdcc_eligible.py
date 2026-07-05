from policyengine_us.model_api import *


class count_cdcc_eligible(Variable):
    value_type = int
    entity = TaxUnit
    label = "CDCC qualifying individuals"
    unit = "person"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21#b_1"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_eligible = person("is_cdcc_eligible", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # A married couple contributes at most one qualifying individual via
        # the spouse prong (IRC 21(b)(1)(C)): the taxpayer is never their own
        # qualifying individual, so two incapacitated spouses count as one.
        dependent_count = tax_unit.sum(is_eligible & ~head_or_spouse)
        has_eligible_spouse = tax_unit.any(is_eligible & head_or_spouse)
        return dependent_count + has_eligible_spouse
