from policyengine_us.model_api import *


class ct_tfa_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Connecticut Temporary Family Assistance (TFA)"
    definition_period = MONTH
    reference = "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/state-plans-and-federal-reports/tanf-state-plan/ct-tanf-state-plan-2024---2026---41524-amendment.pdf#page=10"
    defined_for = StateCode.CT

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        immigration_status_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        resources_eligible = spm_unit("ct_tfa_resources_eligible", period)
        income_eligible = spm_unit("ct_tfa_income_eligible", period)
        return (
            demographic_eligible
            & immigration_status_eligible
            & resources_eligible
            & income_eligible
        )
