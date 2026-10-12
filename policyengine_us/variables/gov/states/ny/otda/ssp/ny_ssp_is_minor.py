from policyengine_us.model_api import *


class ny_ssp_is_minor(Variable):
    value_type = bool
    entity = Person
    label = "Minor for New York State Supplement Program living arrangements"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-2.1"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.otda.ssp
        age = person("age", period)
        student = person("ny_ssp_regularly_attends_school", period)
        return (age < p.minor_age) | (
            (age < p.student_minor_age)
            & student
            & ~person.family("is_married", period)
            & ~person("is_household_head", period)
        )
