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
        # The calc returns false for both under 5 AND 15+, so we need to check age is in child range
        # Get the upper age limit from the last threshold in the parameter
        max_child_age = p.child.thresholds[-1]
        return (age < max_child_age) & ~p.child.calc(age)
