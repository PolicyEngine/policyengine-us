from policyengine_us.model_api import *


class nc_sa_rate(Variable):
    value_type = float
    entity = Person
    label = "North Carolina SA monthly rate"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NC
    reference = (
        # PDF pages 204-205
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-Manual-Rev-June-2026.pdf#page=204",
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-In-Home-Program-Manual-Rev-June-2026.pdf#page=40",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.sa.rate
        setting = person("nc_sa_care_setting", period)
        settings = setting.possible_values
        enhanced = (setting == settings.SPECIAL_CARE_UNIT) | (
            setting == settings.IN_HOME_ENHANCED
        )
        published_rate = where(enhanced, p.enhanced, p.basic)
        facility = (setting == settings.ADULT_CARE_HOME) | (
            setting == settings.SPECIAL_CARE_UNIT
        )
        # A facility may charge an SA resident less than the published rate;
        # the actual rate is then used in the budget (SA-3220 II.A).
        contracted_rate = person("nc_sa_facility_rate", period)
        lower_rate = facility & (contracted_rate > 0)
        return where(lower_rate, min_(contracted_rate, published_rate), published_rate)
