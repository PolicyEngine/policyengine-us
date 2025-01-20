from policyengine_us.model_api import *

class slspc_baseline_base_cost(Variable):
    value_type = float
    entity = Person
    label = "Second-lowest ACA silver-plan base cost"
    documentation = "Second-lowest ACA silver-plan cost at age 0"
    unit = USD
    definition_period = MONTH

    def formula(Person, period, parameters):
        # Get state code and rating area
        state_code = Person("state_code", period)
        rating_area = Person("slspc_rating_area", period)

        # Access the baseline costs from parameters
        baseline_costs = parameters.gov.aca.state_ratingarea_cost

        # Return the cost for the specific state and rating area
        return baseline_costs[state_code][rating_area]