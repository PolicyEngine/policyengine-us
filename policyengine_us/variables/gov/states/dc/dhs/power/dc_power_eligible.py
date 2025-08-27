from policyengine_us.model_api import *


class dc_power_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for DC Program on Work, Employment, and Responsibility (POWER)"
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.72",
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.72a",
    )
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        has_eligible_head_or_spouse = (
            add(spm_unit, period, ["dc_power_head_or_spouse_eligible"]) > 0
        )
        meets_basic_eligibility_requirements = spm_unit(
            "dc_tanf_basic_eligibility_requirements", period
        )
        has_disqualifying_benefits = spm_unit(
            "dc_power_has_disqualifying_benefits", period
        )

        return (
            has_eligible_head_or_spouse
            & meets_basic_eligibility_requirements
            & ~has_disqualifying_benefits
        )
