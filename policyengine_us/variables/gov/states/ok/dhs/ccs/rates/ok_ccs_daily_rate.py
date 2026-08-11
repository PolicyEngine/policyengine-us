from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ok.dhs.ccs.rates.ok_ccs_provider_setting import (
    OKCCSProviderSetting,
)


class ok_ccs_daily_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Oklahoma Child Care Subsidy daily rate per child"
    definition_period = MONTH
    defined_for = "ok_ccs_eligible_child"
    reference = "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-4-b.pdf#page=3"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ok.dhs.ccs.rates
        provider_setting = person("ok_ccs_provider_setting", period)
        star_level = person("ok_ccs_star_level", period)
        time_category = person("ok_ccs_time_category", period)
        center_age_group = person("ok_ccs_center_age_group", period)
        home_age_group = person("ok_ccs_home_age_group", period)
        center_rate = p.center[star_level][center_age_group][time_category]
        home_rate = p.home[star_level][home_age_group][time_category]
        # Care in the child's own home is paid at 90 percent of the one-star
        # child care home rate for a child of the same age (Appendix C-4-B).
        in_home_rate = (
            p.home.STAR_1[home_age_group][time_category] * p.in_home_rate_ratio
        )
        return select(
            [
                provider_setting == OKCCSProviderSetting.CHILD_CARE_CENTER,
                provider_setting == OKCCSProviderSetting.CHILD_CARE_HOME,
                provider_setting == OKCCSProviderSetting.IN_HOME,
            ],
            [center_rate, home_rate, in_home_rate],
        )
