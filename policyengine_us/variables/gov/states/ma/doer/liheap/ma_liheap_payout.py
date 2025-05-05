from policyengine_us.model_api import *


class ma_liheap_payout(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    defined_for = StateCode.MA
    label = "Massachusetts LIHEAP Payout"

    def formula(spm_unit, period, parameters):
        utility_type = spm_unit("ma_liheap_utility_type", period)
        benefit_level = spm_unit("ma_liheap_benefit_level", period)
        is_subsidized = spm_unit(
            "ma_liheap_subsidized_housing_eligible", period
        )
        hecs_threshold = spm_unit("ma_liheap_hecs_threshold", period)

        p = parameters(period).gov.states.ma.doer.liheap

        # CASE 1: Utility type is HEC
        hec_payout = where(
            utility_type == "HEC",
            where(
                hecs_threshold,
                where(
                    is_subsidized,
                    p.payout.subsidized[benefit_level]["HEC"],
                    p.payout.non_subsidized[benefit_level]["HEC"],
                ),
                0,  # If HEC threshold not met
            ),
            0,  # Not HEC case; handled separately below
        )

        # CASE 2: Utility type is anything else (not HEC)
        other_payout = where(
            utility_type != "HEC",
            where(
                is_subsidized,
                p.payout.subsidized[benefit_level][utility_type],
                p.payout.non_subsidized[benefit_level][utility_type],
            ),
            0,  # If utility_type is HEC, fallback here
        )

        # Return appropriate payout
        return hec_payout + other_payout