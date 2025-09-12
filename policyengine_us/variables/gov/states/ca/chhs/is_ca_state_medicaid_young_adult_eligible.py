from policyengine_us.model_api import *


class is_ca_state_medicaid_young_adult_eligible(Variable):
    value_type = bool
    entity = Person
    label = "California state-funded Medicaid young adult eligible"
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.chhs.young_adult
        age = person("age", period)
        is_young_adult = p.age_range.calc(age)
        is_eligible_period = p.eligible

        return is_young_adult & is_eligible_period
