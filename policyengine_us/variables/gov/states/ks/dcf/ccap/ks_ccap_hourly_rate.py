from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ks.dcf.ccap.ks_ccap_provider_type import (
    KSCCAPProviderType,
)


class ks_ccap_hourly_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Kansas CCAP maximum hourly provider rate"
    definition_period = MONTH
    defined_for = "ks_ccap_eligible_child"
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/appendix/c-18_providerratecht.pdf#page=8"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ks.dcf.ccap.rates
        provider_type = person("ks_ccap_provider_type", period)
        rate_group = person.household("ks_ccap_rate_group", period.this_year)
        center_age = person("ks_ccap_center_age_group", period)
        home_age = person("ks_ccap_home_age_group", period)
        relative_age = person("ks_ccap_relative_age_group", period)

        center_rate = p.center[rate_group][center_age]
        licensed_home_rate = p.licensed_home[rate_group][home_age]
        out_of_home_relative_rate = p.out_of_home_relative[rate_group][relative_age]
        # In-home relative care and the enhanced special-care rate are flat
        # statewide hourly maximums (C-18 footer).
        in_home_relative_rate = p.in_home_relative
        enhanced_special_care_rate = p.enhanced_special_care

        types = KSCCAPProviderType
        return select(
            [
                provider_type == types.CENTER,
                provider_type == types.LICENSED_HOME,
                provider_type == types.OUT_OF_HOME_RELATIVE,
                provider_type == types.IN_HOME_RELATIVE,
                provider_type == types.ENHANCED_SPECIAL_CARE,
            ],
            [
                center_rate,
                licensed_home_rate,
                out_of_home_relative_rate,
                in_home_relative_rate,
                enhanced_special_care_rate,
            ],
        )
