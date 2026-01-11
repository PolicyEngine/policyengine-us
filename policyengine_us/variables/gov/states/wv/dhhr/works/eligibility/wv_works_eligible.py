from policyengine_us.model_api import *


class wv_works_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for West Virginia WV Works"
    definition_period = MONTH
    reference = "https://code.wvlegislature.gov/9-9/"
    defined_for = StateCode.WV

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("wv_works_income_eligible", period)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        resources_eligible = spm_unit("wv_works_resources_eligible", period)
        # Immigration eligibility per WV IMM Chapter 18
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        return (
            income_eligible
            & demographic_eligible
            & resources_eligible
            & immigration_eligible
        )
