from policyengine_us.model_api import *


class il_pi_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Child meets age requirements for Illinois PI"
    definition_period = YEAR
    reference = "https://www.isbe.net/Pages/Birth-to-Age-3-Years.aspx"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Children under age 3 (birth to age 3) are eligible.
        p = parameters(period).gov.states.il.isbe.pi.eligibility.age
        age = person("age", period)
        return age < p.maximum
