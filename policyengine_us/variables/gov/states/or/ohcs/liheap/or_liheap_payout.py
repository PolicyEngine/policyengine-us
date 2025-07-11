from policyengine_us.model_api import *


class or_liheap_payout(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    defined_for = "or_liheap_eligibility"
    label = "Oregon LIHEAP Payout"

    def formula(spm_unit, period, parameters):
        utility_type = spm_unit("utility_type", period)
        unit_size = clip(spm_unit("spm_unit_size", period), 1, 6)
        benefit_level = spm_unit("or_liheap_benefit_level", period)
        is_region1 = spm_unit("or_liheap_in_region_one", period)
        electricity_type = spm_unit("or_liheap_electricity_type", period)

        p = parameters(period).gov.states["or"].ohcs.liheap

        # Applies multiplier to the payout when electricity is used for both heating and cooling (not an official policy parameter).
        electricity_multiplier = where(
            (utility_type == utility_type.possible_values.ELECTRICITY)
            & (
                electricity_type
                == electricity_type.possible_values.HEATING_AND_COOLING
            ),
            2,
            1,
        )

        payout = where(
            is_region1,
            p.payout.or_liheap_region_one[unit_size][benefit_level][
                utility_type
            ],
            p.payout.or_liheap_region_two[unit_size][benefit_level][
                utility_type
            ],
        )
        utility_expense = add(
            spm_unit,
            period,
            [
                "electricity_expense",
                "fuel_oil_expense",  # heating oil expense
                "gas_expense",  # liquid gas expense
                "wood_pellets_expense",
                "natural_gas_expense",
            ],
        )

        return min_(payout * electricity_multiplier, utility_expense)
