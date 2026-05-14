from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wv.dhhr.ccap.wv_ccap_provider_type import (
    WVCCAPProviderType,
)


class wv_ccap_daily_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "West Virginia CCAP daily provider reimbursement rate"
    definition_period = MONTH
    defined_for = "wv_ccap_eligible_child"
    reference = "https://bfa.wv.gov/media/6831/download?inline"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wv.dhhr.ccap.rates
        provider_type = person("wv_ccap_provider_type", period)
        quality_tier = person("wv_ccap_quality_tier", period)
        age_category = person("wv_ccap_child_age_category", period)
        informal_age = person("wv_ccap_informal_age_group", period)

        family_home_rate = p.family_home[quality_tier][age_category]
        family_facility_rate = p.family_facility[quality_tier][age_category]
        center_rate = p.center[quality_tier][age_category]
        out_of_school_rate = p.out_of_school_time
        informal_rate = p.informal_relative[informal_age]

        types = WVCCAPProviderType
        return select(
            [
                provider_type == types.FAMILY_HOME,
                provider_type == types.FAMILY_FACILITY,
                provider_type == types.CENTER,
                provider_type == types.OUT_OF_SCHOOL_TIME,
                provider_type == types.INFORMAL_RELATIVE,
            ],
            [
                family_home_rate,
                family_facility_rate,
                center_rate,
                out_of_school_rate,
                informal_rate,
            ],
        )
