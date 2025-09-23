from policyengine_us.model_api import *


class tx_dart_free_ride_benefit(Variable):
    value_type = float
    entity = Person
    label = "Dallas Area Rapid Transit (DART) free ride benefit value"
    unit = USD
    definition_period = YEAR
    defined_for = "tx_dart_free_ride_eligible_young_child"
    reference = (
        "https://www.dart.org/fare/general-fares-and-overview/reduced-fares"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tx.dart.monthly_pass_cost
        # Currently only include the monthly pass costs
        return p.full_fare * MONTHS_IN_YEAR
