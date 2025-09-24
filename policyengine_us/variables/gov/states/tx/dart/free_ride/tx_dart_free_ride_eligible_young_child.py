from policyengine_us.model_api import *


class tx_dart_free_ride_eligible_young_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible young child for Dallas Area Rapid Transit (DART) Free Ride program"
    definition_period = YEAR
    defined_for = StateCode.TX
    reference = (
        "https://www.dart.org/fare/general-fares-and-overview/reduced-fares"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tx.dart.reduced_fare.age_threshold
        age = person("age", period)
        # Under 5 years old - children under 5 ride free
        # The child parameter scale returns false for ages < 5 (meaning free ride)
        # and true for ages 5-14 (meaning reduced fare)
        # Since we want children who get free rides, we check for false result and age < 15
        return (age < 15) & ~p.child.calc(age)
