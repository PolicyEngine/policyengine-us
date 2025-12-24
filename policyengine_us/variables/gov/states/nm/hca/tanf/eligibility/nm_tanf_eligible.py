from policyengine_us.model_api import *


class nm_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Mexico TANF eligible"
    definition_period = MONTH
    reference = "https://www.srca.nm.gov/parts/title08/08.102.0400.html"
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        # Per 8.102 NMAC, eligibility requires:
        # 1. Demographic eligibility (federal baseline)
        # 2. Immigration eligibility (federal baseline)
        # 3. Gross income under 85% FPL
        # 4. Net income under standard of need
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        gross_income_eligible = spm_unit(
            "nm_tanf_gross_income_eligible", period
        )
        net_income_eligible = spm_unit("nm_tanf_net_income_eligible", period)

        return (
            demographic_eligible
            & immigration_eligible
            & gross_income_eligible
            & net_income_eligible
        )
