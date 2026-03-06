from policyengine_us.model_api import *


class slcsp_age_0(Variable):
    value_type = float
    entity = Household
    label = "Second-lowest ACA silver-plan for a person aged 0"
    unit = USD
    definition_period = MONTH

    def formula(household, period, parameters):
        # Get state code and rating area
        state_code = household("state_code", period)
        rating_area = household("slcsp_rating_area", period)

        # Access the baseline costs from parameters
        p = parameters(period).gov.aca

        # Rating area 0 means unknown (e.g. no zip code data available)
        known = rating_area > 0
        safe_rating_area = where(known, rating_area, 1)
        cost = p.state_rating_area_cost[state_code][safe_rating_area]
        return where(known, cost, 0)
