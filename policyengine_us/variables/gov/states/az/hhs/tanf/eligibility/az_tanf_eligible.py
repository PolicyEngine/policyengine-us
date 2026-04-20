from policyengine_us.model_api import *


class az_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Arizona TANF"
    definition_period = MONTH
    reference = "https://www.azleg.gov/ars/46/00292.htm"
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        # Use federal demographic eligibility (minor child or pregnant)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        # Must be US citizen or qualified alien
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        income_eligible = spm_unit("az_tanf_income_eligible", period)
        resources_eligible = spm_unit("az_tanf_resources_eligible", period)

        return (
            demographic_eligible
            & immigration_eligible
            & income_eligible
            & resources_eligible
        )
