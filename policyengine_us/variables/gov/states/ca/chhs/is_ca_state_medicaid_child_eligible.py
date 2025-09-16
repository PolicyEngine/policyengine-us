from policyengine_us.model_api import *


class is_ca_state_medicaid_child_eligible(Variable):
    value_type = bool
    entity = Person
    label = "California state-funded Medicaid child eligible"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.chhs.child
        age = person("age", period)
        is_child = p.age_range.calc(age)
        is_eligible_period = p.eligible

        return is_child & is_eligible_period
