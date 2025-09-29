from policyengine_us.model_api import *


class tx_dart_reduced_fare_benefit(Variable):
    value_type = float
    entity = Person
    label = "Dallas Area Rapid Transit (DART) reduced fare benefit value"
    unit = USD
    definition_period = YEAR
    defined_for = "tx_dart_reduced_fare_eligible"
    reference = (
        "https://www.dart.org/fare/general-fares-and-overview/reduced-fares"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tx.dart.monthly_pass_cost
        return (p.full_fare - p.reduced_fare) * MONTHS_IN_YEAR
