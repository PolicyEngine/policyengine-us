from policyengine_us.model_api import *


class ok_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Oklahoma TANF"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/oklahoma/title-340/chapter-10"
    )
    defined_for = StateCode.OK

    def formula(spm_unit, period, parameters):
        # Use federal demographic eligibility (minor child or pregnant)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        # Per OAC 340:10-15: Must be US citizen or qualified alien
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        income_eligible = spm_unit("ok_tanf_income_eligible", period)
        resources_eligible = spm_unit("ok_tanf_resources_eligible", period)

        return (
            demographic_eligible
            & immigration_eligible
            & income_eligible
            & resources_eligible
        )
