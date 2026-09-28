from policyengine_us.model_api import *


class ks_liheap_matrix_amount(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Kansas LIEAP benefit matrix amount"
    documentation = "Annual benefit from the Kansas LIEAP benefit matrix for the household's primary heating fuel, one-month income band, utility rate tier, dwelling type and household size group, before the minimum benefit."
    unit = USD
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/KS_BenefitMatrix_2026.pdf#page=1",
        "https://liheapch.acf.gov/docs/2025/benefits-matricies/KS_BenefitMatrix_2025.pdf#page=1",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm13400.htm",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ks.dcf.liheap.payment.matrix
        fuel = spm_unit("ks_liheap_fuel_category", period)
        fuels = fuel.possible_values
        # State-masked helpers return zero outside Kansas. Keep lookup keys
        # valid while the framework evaluates mixed-state arrays.
        band = max_(spm_unit("ks_liheap_income_band", period), 1)
        tier = spm_unit("ks_liheap_utility_rate_tier", period)
        dwelling = spm_unit("ks_liheap_dwelling_type", period)
        size_group = max_(spm_unit("ks_liheap_household_size_group", period), 1)
        return select(
            [
                fuel == fuels.NATURAL_GAS,
                fuel == fuels.ELECTRICITY,
                fuel == fuels.PROPANE,
                fuel == fuels.OTHER,
            ],
            [
                p.natural_gas[band][tier][dwelling][size_group],
                p.electricity[band][tier][dwelling][size_group],
                p.propane[band][tier][dwelling][size_group],
                p.other[band][dwelling][size_group],
            ],
            default=0,
        )
