from policyengine_us.model_api import *


class is_cdcc_eligible(Variable):
    value_type = bool
    entity = Person
    label = "CDCC-eligible"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21#b_1"

    def formula(person, period, parameters):
        age = person("age", period)
        # Subsection A.
        max_age = parameters(period).gov.irs.credits.cdcc.eligibility.child_age
        qualifies_by_age = age < max_age
        # Subsection B (dependent) and C (spouse).
        non_head = ~person("is_tax_unit_head", period)
        disabled = person("incapable_of_self_care", period)
        qualifies_by_disability = non_head & disabled
        return qualifies_by_age | qualifies_by_disability
