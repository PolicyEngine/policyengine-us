from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nj.njdhs.ccap.nj_ccap_provider_type import (
    NJCCAPProviderType,
)


class nj_ccap_maximum_weekly_benefit(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "New Jersey CCAP maximum weekly benefit per child"
    definition_period = MONTH
    defined_for = "nj_ccap_eligible_child"
    reference = "https://www.childcarenj.gov/ChildCareNJ/media/media_library/Max_CC_Payment_Rates.pdf#page=1"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.njdhs.ccap.rates
        provider_type = person("nj_ccap_provider_type", period)
        time_category = person("nj_ccap_time_category", period)
        age_group = person("nj_ccap_age_group", period)
        grow_nj_kids_rating = person("nj_ccap_grow_nj_kids_rating", period)

        center_rate = p.licensed_center[time_category][grow_nj_kids_rating][age_group]
        family_rate = p.registered_family[time_category][grow_nj_kids_rating][age_group]
        home_rate = p.approved_home[time_category][age_group]
        camp_rate = p.aca_summer_camp[time_category][age_group]

        return select(
            [
                provider_type == NJCCAPProviderType.LICENSED_CENTER,
                provider_type == NJCCAPProviderType.REGISTERED_FAMILY,
                provider_type == NJCCAPProviderType.APPROVED_HOME,
                provider_type == NJCCAPProviderType.ACA_SUMMER_CAMP,
            ],
            [
                center_rate,
                family_rate,
                home_rate,
                camp_rate,
            ],
            default=center_rate,
        )
