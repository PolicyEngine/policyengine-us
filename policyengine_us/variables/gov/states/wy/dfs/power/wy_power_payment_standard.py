from policyengine_us.model_api import *


class wy_power_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wyoming POWER payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/table-ii-power-income-limits/",
        "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/",
    )
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wy.dfs.power.payment_standard
        unit_size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(unit_size, p.max_unit_size)
        shelter_qualified = spm_unit("wy_power_shelter_qualified", period)
        # Per Section 905: Two payment schedules based on shelter status
        # Per Table II: Sizes 7-12 have same payment standard
        return where(
            shelter_qualified,
            p.shelter_qualified[capped_size],
            p.shelter_disqualified[capped_size],
        )
