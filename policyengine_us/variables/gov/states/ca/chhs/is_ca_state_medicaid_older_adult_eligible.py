from policyengine_us.model_api import *


class is_ca_state_medicaid_older_adult_eligible(Variable):
    value_type = bool
    entity = Person
    label = "California state-funded Medicaid older adult eligible"
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.chhs.older_adult
        age = person("age", period)
        is_older_adult = p.age_range.calc(age)
        is_eligible_period = p.eligible

        return is_older_adult & is_eligible_period
