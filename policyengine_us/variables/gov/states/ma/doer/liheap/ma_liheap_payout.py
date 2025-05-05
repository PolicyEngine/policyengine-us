from policyengine_us.model_api import *


class ma_liheap_payout(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    defined_for = "ma_liheap_eligible"
    label = "Massachusetts LIHEAP Payout"

    def formula(spm_unit, period, parameters):
        utility_type = spm_unit("ma_liheap_utility_type", period)
        benefit_level = spm_unit("ma_liheap_benefit_level", period)
        is_subsidized = spm_unit("receives_housing_assistance", period)
        hecs_eligible = spm_unit("ma_liheap_hecs_eligible", period)

        p = parameters(period).gov.states.ma.doer.liheap

        # CASE 1: Utility type is HECS
        hec_payout = where(
            utility_type == "HECS",
            where(
                hecs_eligible,
                where(
                    is_subsidized,
                    p.payout.subsidized[benefit_level]["HECS"],
                    p.payout.non_subsidized[benefit_level]["HECS"],
                ),
                0,  # If HEC threshold not met
            ),
            0,  # Not HEC case; handled separately below
        )

        # CASE 2: Utility type is anything else (not HECS)
        other_payout = where(
            utility_type != "HECS",
            where(
                is_subsidized,
                p.payout.subsidized[benefit_level][utility_type],
                p.payout.non_subsidized[benefit_level][utility_type],
            ),
            0,  # If utility_type is HECS, fallback here
        )

        # Return appropriate payout
        return hec_payout + other_payout
# TODO: Remove HECS from utility type