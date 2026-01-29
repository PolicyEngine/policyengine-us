from policyengine_us.model_api import *


class ny_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New York TANF eligible"
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = (
        "https://otda.ny.gov/policy/tanf/TANF-State-Plan-2024-2026.pdf#page=7"
    )

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        income_eligible = spm_unit("ny_tanf_income_eligible", period)
        asset_eligible = spm_unit("ny_tanf_resources_eligible", period)
        return (
            demographic_eligible
            & immigration_eligible
            & income_eligible
            & asset_eligible
        )
