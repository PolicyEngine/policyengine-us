from policyengine_us.model_api import *


class la_fitap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Louisiana FITAP eligible"
    definition_period = MONTH
    reference = (
        "https://www.doa.la.gov/media/tp3lmkyg/67.pdf#page=37",
        "https://www.doa.la.gov/media/tp3lmkyg/67.pdf#page=38",
    )
    defined_for = StateCode.LA

    def formula(spm_unit, period, parameters):
        # Per LAC 67:III.1221: Child must be under 18 or 18 and in school
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)

        # Per LAC 67:III.1223: Must be US citizen or qualified alien
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )

        # Per LAC 67:III.1229: Countable income <= flat grant
        income_eligible = spm_unit("la_fitap_income_eligible", period)

        return demographic_eligible & immigration_eligible & income_eligible
