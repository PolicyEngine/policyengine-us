from policyengine_us.model_api import *


class slcsp_age_0(Variable):
    value_type = float
    entity = Household
    label = "Second-lowest ACA silver-plan for a person aged 0"
    unit = USD
    definition_period = MONTH
    documentation = (
        "The benchmark premium in the model's 2018 age-zero normalization. "
        "For 2014 through 2017, estimate each rating area's premium from its "
        "2018 value times the national benchmark index ratio. Historical "
        "age-curve multipliers retain this normalization."
    )
    reference = (
        "https://www.kff.org/affordable-care-act/state-indicator/marketplace-average-benchmark-premiums/",
        "https://www.kff.org/interactive/subsidy-calculator/",
    )

    def formula_2014(household, period, parameters):
        state_code = household("state_code", period)
        rating_area = household("slcsp_rating_area", period)
        known = rating_area > 0
        safe_rating_area = where(known, rating_area, 1)
        base = parameters("2018-01-01").gov.aca
        cost = base.state_rating_area_cost[state_code][safe_rating_area]
        index = parameters(period).gov.aca.benchmark_premium_uprating
        return where(known, cost * index / base.benchmark_premium_uprating, 0)

    def formula_2018(household, period, parameters):
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
