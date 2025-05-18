from policyengine_us.model_api import *


class il_cta_benefit(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Illinois Chicago Transit Authority benefit amount"
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = "https://www.transitchicago.com/fares/"

    def formula(person, period, parameters):
        free_ride_benefit = person("il_cta_free_ride_benefit", period)
        reduced_fare_benefit = person("il_cta_reduced_fare_benefit", period)

        return max_(free_ride_benefit, reduced_fare_benefit)
