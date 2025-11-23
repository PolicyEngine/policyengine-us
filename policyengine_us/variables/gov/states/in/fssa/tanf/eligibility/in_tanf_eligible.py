from policyengine_us.model_api import *


class in_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana TANF eligible"
    definition_period = MONTH
    reference = (
        "https://iga.in.gov/laws/2023/ic/titles/12",
        "https://iar.iga.in.gov/latestArticle/470/10.3",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        # Demographic eligibility - use federal baseline
        # Per IC 12-14-1-0.5 and 470 IAC 10.3-3
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)

        # Income eligibility - state-specific
        income_eligible = spm_unit("in_tanf_income_eligible", period)

        return demographic_eligible & income_eligible
