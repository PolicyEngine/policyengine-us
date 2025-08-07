from policyengine_us.model_api import *


class il_cta_reduced_fare_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Illinois Chicago Transit Authority Reduced Fare Program"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://www.transitchicago.com/reduced-fare-programs/"

    def formula(person, period, parameters):
        children_reduced_fare = person(
            "il_cta_children_reduced_fare_eligible", period
        )
        rta_reduced_fare = person("il_cta_rta_reduced_fare_eligible", period)
        student_reduced_fare = person(
            "il_cta_student_reduced_fare_eligible", period
        )
        return children_reduced_fare | rta_reduced_fare | student_reduced_fare
