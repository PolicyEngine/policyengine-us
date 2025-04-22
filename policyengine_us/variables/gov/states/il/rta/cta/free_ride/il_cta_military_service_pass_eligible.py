from policyengine_us.model_api import *


class il_cta_military_service_pass_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Illinois Chicago Transit Authority military service pass"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://www.transitchicago.com/military/"

    # def formula(person, period, parameters):
    #     is_in_active_duty
    #     disabled_veterans
    #     return is_in_active_duty | disabled_veterans
