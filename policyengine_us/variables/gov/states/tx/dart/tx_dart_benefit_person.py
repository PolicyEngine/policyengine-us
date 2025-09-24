from policyengine_us.model_api import *


class tx_dart_benefit_person(Variable):
    value_type = float
    entity = Person
    label = "Dallas Area Rapid Transit (DART) benefit value per person"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.TX
    reference = (
        "https://www.dart.org/fare/general-fares-and-overview/reduced-fares"
    )

    def formula(person, period, parameters):
        free_ride_benefit = person("tx_dart_free_ride_benefit", period)
        reduced_fare_benefit = person("tx_dart_reduced_fare_benefit", period)
        return max_(free_ride_benefit, reduced_fare_benefit)
