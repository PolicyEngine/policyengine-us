from policyengine_us.model_api import *


class sc_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the South Carolina TANF program"
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = "https://www.law.cornell.edu/regulations/south-carolina/S.C.-Code-Regs.-114-1140"

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        income_eligible = spm_unit("sc_tanf_income_eligible", period)
        resource_eligible = spm_unit("sc_tanf_resources_eligible", period)
        return (
            demographic_eligible
            & immigration_eligible
            & income_eligible
            & resource_eligible
        )
