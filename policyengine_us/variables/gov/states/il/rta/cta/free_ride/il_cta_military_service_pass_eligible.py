from policyengine_us.model_api import *


class il_cta_military_service_pass_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Illinois Chicago Transit Authority military service pass"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://www.transitchicago.com/military/"

    def formula(person, period, parameters):
        is_in_active_duty = person("military_basic_pay", period) > 0
        # NOTE: The CTA covers a veteran with VA disability compensation "of
        # 10% or greater". The model has no input for ratings below 100%, so
        # veterans rated 10% to 90% are missed.
        disabled_veterans = person(
            "is_fully_disabled_service_connected_veteran", period
        )
        return is_in_active_duty | disabled_veterans
