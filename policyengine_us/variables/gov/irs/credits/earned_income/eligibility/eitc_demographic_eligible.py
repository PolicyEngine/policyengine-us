from policyengine_us.model_api import *


class eitc_demographic_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Meets demographic eligibility for EITC"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/32#c_1_A"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        has_child = tax_unit("tax_unit_children", period) > 0
        age = person("age", period)
        # Relative parameter reference break branching in some states that
        # modify EITC age limits.
        min_age = parameters.gov.irs.credits.eitc.eligibility.age.min(period)
        max_age = parameters.gov.irs.credits.eitc.eligibility.age.max(period)
        meets_age_requirements = (age >= min_age) & (age <= max_age)
        return has_child | tax_unit.any(meets_age_requirements)
