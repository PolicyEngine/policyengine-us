from policyengine_us.model_api import *


class il_cta_free_ride_benefit(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Illinois Chicago Transit Authority Free Ride Program benefit"
    definition_period = MONTH
    defined_for = "il_cta_free_ride_eligible"
    reference = "https://www.transitchicago.com/fares/"

    adds = ["gov.states.il.rta.cta.monthly_pass_cost.full_fare"]
