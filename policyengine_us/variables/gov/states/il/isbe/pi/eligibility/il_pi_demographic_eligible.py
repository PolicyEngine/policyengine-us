from policyengine_us.model_api import *


class il_pi_demographic_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets demographic requirements for Illinois PI"
    definition_period = YEAR
    reference = "https://www.isbe.net/Pages/Birth-to-Age-3-Years.aspx"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Eligible if child under 3 or pregnant woman.
        p = parameters(period).gov.states.il.isbe.pi.eligibility.age_threshold
        age = person("age", period)
        is_child_under_3 = age < p.child
        is_pregnant = person("is_pregnant", period)
        return is_child_under_3 | is_pregnant
