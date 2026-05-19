from policyengine_us.model_api import *


class lcbp_age_0(Variable):
    value_type = float
    entity = Household
    label = "Lowest-cost ACA bronze-plan for a person aged 0"
    unit = USD
    definition_period = MONTH

    def formula(household, period, parameters):
        state_code = household("state_code", period)
        rating_area = household("slcsp_rating_area", period)

        p = parameters(period).gov.aca.lcbp

        known = rating_area > 0
        safe_rating_area = where(known, rating_area, 1)
        cost = p.state_rating_area_cost[state_code][safe_rating_area]
        return where(known, cost, 0)
