from policyengine_us.model_api import *


class pa_ccw_market_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Pennsylvania CCW MCCA daily rate per child"
    definition_period = MONTH
    defined_for = "pa_ccw_eligible_child"
    reference = "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=32"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.pa.dhs.ccw.rates
        provider_type = person("pa_ccw_provider_type", period)
        age_group = person("pa_ccw_age_group", period)
        time_category = person("pa_ccw_time_category", period)
        region = person.household("pa_ccw_region", period.this_year)

        def rate_for_region(region_param):
            return region_param[provider_type][age_group][time_category]

        return select(
            [region == r for r in range(1, 20)],
            [rate_for_region(getattr(p, f"region_{r}")) for r in range(1, 20)],
        )
