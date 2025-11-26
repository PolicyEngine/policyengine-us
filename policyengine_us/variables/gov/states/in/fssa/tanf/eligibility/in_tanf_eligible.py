from policyengine_us.model_api import *


class in_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana TANF eligible"
    definition_period = MONTH
    reference = "https://iar.iga.in.gov/code/2026/470/10.3"  # 470 IAC 10.3
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        # Demographic eligibility - use federal baseline
        # Per IC 12-14-1-0.5 and 470 IAC 10.3-3
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)

        # Immigration eligibility - must have at least one citizen or qualified noncitizen
        # Per IC 12-14-1-1
        person = spm_unit.members
        immigration_eligible = spm_unit.any(
            person("is_citizen_or_legal_immigrant", period.this_year)
        )

        # Income eligibility - state-specific
        income_eligible = spm_unit("in_tanf_income_eligible", period)

        # Resources eligibility - state-specific
        # Per 470 IAC 10.3-3-6
        resources_eligible = spm_unit("in_tanf_resources_eligible", period)

        return (
            demographic_eligible
            & immigration_eligible
            & income_eligible
            & resources_eligible
        )
