from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ak.dpa.ccap.rates.ak_ccap_provider_type import (
    AKCCAPProviderType,
)


class ak_ccap_max_provider_rate_per_child(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Alaska CCAP maximum provider reimbursement rate per child"
    definition_period = MONTH
    defined_for = "ak_ccap_child_eligible"
    reference = "https://health.alaska.gov/media/wsvhl3v3/ccap-rate-schedule.pdf#page=1"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ak.dpa.ccap.rates
        provider_type = person("ak_ccap_provider_type", period)
        care_unit = person("ak_ccap_care_unit", period)
        age_group = person("ak_ccap_age_group", period)
        region = person.spm_unit("ak_ccap_rate_region", period)

        center_rate = p.licensed_center[care_unit][region][age_group]
        group_home_rate = p.licensed_group_home[care_unit][region][age_group]
        home_rate = p.licensed_home[care_unit][region][age_group]
        relative_rate = p.approved_relative_in_home[care_unit][region][age_group]

        return select(
            [
                provider_type == AKCCAPProviderType.LICENSED_CENTER,
                provider_type == AKCCAPProviderType.LICENSED_GROUP_HOME,
                provider_type == AKCCAPProviderType.LICENSED_HOME,
                provider_type == AKCCAPProviderType.APPROVED_RELATIVE_IN_HOME,
            ],
            [
                center_rate,
                group_home_rate,
                home_rate,
                relative_rate,
            ],
        )
