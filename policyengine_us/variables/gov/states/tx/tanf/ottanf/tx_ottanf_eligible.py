from policyengine_us.model_api import *


class tx_ottanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Texas One-Time TANF (OTTANF)"
    definition_period = YEAR
    reference = "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-2410-general-policy"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Must meet regular TANF eligibility requirements
        tanf_eligible = spm_unit("tx_tanf_eligible", period.first_month)

        # Income must be at or below 200% FPL
        income_eligible = spm_unit(
            "tx_ottanf_income_eligible", period.first_month
        )

        # Resources must be at or below $1,000
        resources_eligible = spm_unit(
            "tx_tanf_resources_eligible", period.first_month
        )

        # Cannot currently receive TANF
        # Simplified: assuming not receiving if benefit is 0
        tanf_benefit = add(spm_unit, period, ["tx_tanf"])
        not_receiving_tanf = tanf_benefit == 0

        # All conditions must be met
        return (
            tanf_eligible
            & income_eligible
            & resources_eligible
            & not_receiving_tanf
        )
