from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ri.dhs.ccap.ri_ccap_provider_type import (
    RICCAPProviderType,
)


class ri_ccap_maximum_weekly_benefit(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Rhode Island CCAP maximum weekly benefit per child"
    definition_period = MONTH
    defined_for = "ri_ccap_eligible_child"
    reference = (
        "https://dhs.ri.gov/media/9356/download?language=en",
        "https://dhs.ri.gov/media/7481/download?language=en",
        "https://dhs.ri.gov/media/3556/download?language=en",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ri.dhs.ccap.rates
        provider_type = person("ri_ccap_provider_type", period)
        time_category = person("ri_ccap_time_category", period)

        center_age = person("ri_ccap_center_age_group", period)
        star_rating = person("ri_ccap_star_rating", period)
        center_rate = p.center[time_category][star_rating][center_age]

        family_age = person("ri_ccap_family_age_group", period)
        family_rate = p.family[time_category][star_rating][family_age]

        step_rating = person("ri_ccap_step_rating", period)
        exempt_rate = p.exempt[time_category][step_rating][family_age]

        return select(
            [
                provider_type == RICCAPProviderType.LICENSED_CENTER,
                provider_type == RICCAPProviderType.LICENSED_FAMILY,
            ],
            [
                center_rate,
                family_rate,
            ],
            default=exempt_rate,
        )
