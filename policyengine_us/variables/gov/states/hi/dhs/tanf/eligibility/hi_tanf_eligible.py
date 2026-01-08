from policyengine_us.model_api import *


class hi_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Hawaii TANF"
    definition_period = MONTH
    reference = (
        "https://humanservices.hawaii.gov/wp-content/uploads/2024/12/Hawaii_TANF_State_Plan_Signed_Certified-Eff_20231001.pdf#page=6",
    )
    defined_for = StateCode.HI

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        gross_income_eligible = spm_unit(
            "hi_tanf_gross_income_eligible", period
        )
        # NOTE: Hawaii disregards assets since April 18, 2013
        return (
            demographic_eligible & immigration_eligible & gross_income_eligible
        )
