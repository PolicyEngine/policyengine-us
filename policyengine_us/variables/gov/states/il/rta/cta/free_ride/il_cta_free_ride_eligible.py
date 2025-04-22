from policyengine_us.model_api import *


class il_cta_free_ride_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Eligible for the Illinois Chicago Transit Authority free ride program"
    )
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://www.transitchicago.com/reduced-fare-programs/#free"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.rta.age_threshold
        age = person("age", period)
        senior = age >= p.senior
        disabled = person("disabled", period)
        is_in_dabap = person("il_dabap_eligible", period)
        eligible_senior = senior & is_in_dabap
        eligible_disabled = disabled & is_in_dabap
        eligible_military_status = person(
            "il_cta_military_service_pass_eligible", period
        )
        return eligible_senior | eligible_disabled | eligible_military_status
