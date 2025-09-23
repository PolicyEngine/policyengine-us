from policyengine_us.model_api import *


class tx_dart_free_ride_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Dallas Area Rapid Transit (DART) Free Ride program"
    definition_period = YEAR
    defined_for = StateCode.TX
    reference = (
        "https://www.dart.org/fare/general-fares-and-overview/reduced-fares"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tx.dart.reduced_fare.age_threshold
        age = person("age", period)
        # Under 5 years old
        return age < p.child.thresholds[1]
