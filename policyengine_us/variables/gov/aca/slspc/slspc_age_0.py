from policyengine_us.model_api import *
from policyengine_core.simulations import Simulation


class slspc_age_0(Variable):
    value_type = float
    entity = Household
    label = "Second-lowest ACA silver-plan for a person aged 0"
    unit = USD
    definition_period = MONTH

    def formula(household, period, parameters):
        # Skip if in a microsimulation. [THIS ISN'T WORKING]
        simulation: Simulation = household.simulation
        if simulation.is_over_dataset:
            return 0
        # Get state code and rating area
        state_code = household("state_code", period)
        rating_area = household("slspc_rating_area", period)

        # Access the baseline costs from parameters
        p = parameters(period).gov.aca

        # Return the cost for the specific state and rating area
        return p.state_ratingarea_cost[state_code][rating_area]
