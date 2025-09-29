from policyengine_us.model_api import *


class is_lifeline_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income-eligible for Lifeline"
    documentation = (
        "Meets income requirements for Lifeline (federal or state-expanded)"
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/47/54.409",
        "https://statutes.capitol.texas.gov/Docs/UT/htm/UT.55.htm#55.015",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.fcc.lifeline
        fpg_ratio = spm_unit("fcc_fpg_ratio", period)

        # Some states expand eligibility beyond federal limit
        state = spm_unit.household("state_code_str", period)
        is_tx = state == "TX"

        # Texas expands to 150% FPG per Texas Utilities Code § 55.015(d-1)
        tx_p = parameters(period).gov.states.tx.uct.lifeline

        # Use state-specific limit where applicable, otherwise federal (135%)
        # Convert to float32 to match fpg_ratio dtype for comparison
        # Without this, float32(1.35) > float64(1.35) due to precision differences
        fpg_limit = where(is_tx, tx_p.fpg_limit, p.fpg_limit).astype(
            np.float32
        )

        return fpg_ratio <= fpg_limit
