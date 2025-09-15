from policyengine_us.model_api import *


class is_ca_state_medicaid_adult_eligible(Variable):
    value_type = bool
    entity = Person
    label = "California state-funded Medicaid adult eligible"
    definition_period = YEAR
    defined_for = StateCode.CA
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.chhs.adult
        age = person("age", period)
        is_adult = p.age_range.calc(age)
        is_eligible_period = p.eligible

        return is_adult & is_eligible_period
