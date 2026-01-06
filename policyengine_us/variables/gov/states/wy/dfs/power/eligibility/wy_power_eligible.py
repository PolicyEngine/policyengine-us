from policyengine_us.model_api import *


class wy_power_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wyoming POWER eligible"
    definition_period = MONTH
    reference = "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/"
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        # Use federal demographic eligibility (minor child or pregnant)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        # Per Section 606: Must meet citizenship/alien status requirements
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        income_eligible = spm_unit("wy_power_income_eligible", period)
        resources_eligible = spm_unit("wy_power_resources_eligible", period)

        return (
            demographic_eligible
            & immigration_eligible
            & income_eligible
            & resources_eligible
        )
