from policyengine_us.model_api import *


class wy_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wyoming TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/table-ii-power-income-limits/",
        "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/",
    )
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wy.dfs.tanf
        unit_size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(unit_size, p.max_unit_size)
        shelter_qualified = spm_unit("wy_tanf_shelter_qualified", period)

        # Per Section 905: Two payment schedules based on shelter status
        shelter_qualified_amount = (
            p.benefit.payment_standard.shelter_qualified[capped_size]
        )
        shelter_disqualified_amount = (
            p.benefit.payment_standard.shelter_disqualified[capped_size]
        )

        return where(
            shelter_qualified,
            shelter_qualified_amount,
            shelter_disqualified_amount,
        )
