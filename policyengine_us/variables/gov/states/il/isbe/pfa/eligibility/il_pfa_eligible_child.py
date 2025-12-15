from policyengine_us.model_api import *


class il_pfa_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Child meets age requirements for Illinois PFA"
    definition_period = YEAR
    reference = "https://www.isbe.net/pages/preschool-for-all.aspx"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Children ages 3-5 (before kindergarten) are eligible.
        p = parameters(period).gov.states.il.isbe.pfa.eligibility
        age = person("age", period)
        return p.age_range.calc(age)
