from policyengine_us.model_api import *


class il_cta_free_ride_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Eligible for the Illinois Chicago Transit Authority Free Ride Program"
    )
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://www.transitchicago.com/reduced-fare-programs/#free"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.il.rta.cta.free_ride_program.age_threshold
        age = person("age", period)
        young_child = age <= p.young_child
        bap_eligible = person("il_bap_eligible", period)
        eligible_military_status = person(
            "il_cta_military_service_pass_eligible", period
        )
        return young_child | bap_eligible | eligible_military_status
