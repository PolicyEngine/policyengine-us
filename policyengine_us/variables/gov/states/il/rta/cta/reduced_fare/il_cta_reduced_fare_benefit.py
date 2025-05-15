from policyengine_us.model_api import *


class il_cta_reduced_fare_benefit(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Illinois Chicago Transit Authority Reduced Fare Program benefit"
    definition_period = MONTH
    defined_for = "il_cta_reduced_fare_eligible"
    reference = "https://www.transitchicago.com/fares/"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.rta.cta.monthly_pass_cost
        full_fare_cost = p.full_fare
        reduced_fare_cost = p.reduced_fare
        # Student's regular fare is 1/4 of the full fare, the price for student monthly pass is unavailable
        return full_fare_cost - reduced_fare_cost
