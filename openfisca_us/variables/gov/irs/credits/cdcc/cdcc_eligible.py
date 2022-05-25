from openfisca_us.model_api import *


class cdcc_eligible(Variable):
    value_type = bool
    entity = Person
    label = "CDCC-eligible"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21#b_1"

    def formula(person, period, parameters):
        age = person("age", period)
        max_age = parameters(period).irs.credits.cdcc.eligibility.child_age
        non_head = ~person("is_tax_unit_head", period)
        disabled = person("incapable_of_self_care", period)
        return (age < max_age) | (non_head & disabled)
