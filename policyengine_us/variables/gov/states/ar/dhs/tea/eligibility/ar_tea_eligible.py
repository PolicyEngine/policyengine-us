from policyengine_us.model_api import *


class ar_tea_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Arkansas TEA eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/arkansas/208-00-13-Ark-Code-R-SS-001"
    defined_for = StateCode.AR

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("ar_tea_income_eligible", period)
        resources_eligible = spm_unit("ar_tea_resources_eligible", period)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        # Must have at least one U.S. citizen or qualified immigrant
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        return (
            income_eligible
            & resources_eligible
            & demographic_eligible
            & immigration_eligible
        )
