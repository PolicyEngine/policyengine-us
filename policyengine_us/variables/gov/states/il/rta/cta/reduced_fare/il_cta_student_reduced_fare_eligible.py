from policyengine_us.model_api import *


class il_cta_student_reduced_fare_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Illinois Chicago Transit Authority student reduced fare"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://www.transitchicago.com/reduced-fare-programs/#students"
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.il.rta.cta.reduced_fare_program.age_threshold
        age = person("age", period)
        age_eligible = age <= p.student
        is_student = person("is_in_secondary_school", period)
        return age_eligible & is_student
