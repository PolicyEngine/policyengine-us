from policyengine_us.model_api import *


class ct_tfa_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Connecticut Temporary Family Assistance (TFA)"
    definition_period = MONTH
    reference = "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf?rev=f9c7a2028b6e409689d213d1966d6818&hash=9DDB6100DBC3D983F7946E33D702B2C8#page=10"
    defined_for = StateCode.CT

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        immigration_status_eligible = spm_unit(
            "tanf_eligible_unit_based_on_immigration_status", period
        )
        resources_eligible = spm_unit("ct_tfa_resources_eligible", period)
        income_eligible = spm_unit("ct_tfa_income_eligible", period)
        return (
            demographic_eligible
            & immigration_status_eligible
            & resources_eligible
            & income_eligible
        )
