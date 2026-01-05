from policyengine_us.model_api import *


class la_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Louisiana TANF eligible"
    definition_period = MONTH
    reference = "https://ldh.la.gov/page/fitap"
    defined_for = StateCode.LA

    def formula(spm_unit, period, parameters):
        # Use federal demographic eligibility
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)

        # Must have at least one U.S. citizen or qualified immigrant
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )

        # Income eligibility (countable income <= flat grant)
        income_eligible = spm_unit("la_tanf_income_eligible", period)

        # NOTE: Louisiana excludes all resources from eligibility
        # determination, so no resource test is needed.

        return demographic_eligible & immigration_eligible & income_eligible
