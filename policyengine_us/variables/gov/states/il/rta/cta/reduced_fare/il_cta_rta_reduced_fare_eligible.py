from policyengine_us.model_api import *


class il_cta_rta_reduced_fare_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Eligible for the Illinois Chicago Transit Authority RTA reduced fare"
    )
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://www.transitchicago.com/reduced-fare-programs/#rtareduced"
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.il.rta.cta.reduced_fare_program.age_threshold
        age = person("age", period)
        senior = age >= p.senior
        disabled = person("is_disabled", period)
        medicare_cardholder = person("is_medicare_eligible", period)
        return senior | disabled | medicare_cardholder
