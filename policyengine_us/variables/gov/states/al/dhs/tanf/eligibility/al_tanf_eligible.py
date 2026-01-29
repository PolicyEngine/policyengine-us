from policyengine_us.model_api import *


class al_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Alabama TANF eligibility"
    definition_period = MONTH
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/10/DHR-FAD-595-Oct.23.pdf#page=1"
    defined_for = StateCode.AL

    def formula(spm_unit, period, parameters):
        # Use federal demographic eligibility (minor child or pregnant)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        # Must be US citizen or qualified noncitizen
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        income_eligible = spm_unit("al_tanf_income_eligible", period)
        # Alabama has NO asset limit for TANF

        return demographic_eligible & immigration_eligible & income_eligible
