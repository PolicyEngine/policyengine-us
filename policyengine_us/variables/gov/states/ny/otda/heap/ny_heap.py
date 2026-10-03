from policyengine_us.model_api import *


class ny_heap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP regular heating benefit"
    unit = USD
    defined_for = "ny_heap_eligible"
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/NY_BenefitMatrix_2026.docx",
        # PDF pages 5, 9, 10.
        "https://liheapch.acf.gov/docs/2026/state-plans/NY_Plan_2026.pdf#page=5",
        # PDF pages 45, 46, 47, 48, 49, 84, 87, 88.
        "https://otda.ny.gov/programs/heap/HEAP-manual.pdf#page=45",
    )
    documentation = "Annual regular heating benefit and ordinary Tier I/vulnerability supplements, verified for FY2026. Earlier years are unverified backfilled estimates. Housing assistance approximates subsidized rent (market-rent voucher exceptions are unsupported). Unknown direct-heating fuel returns zero; solar falls within other fuels. No bill cap. Crisis, cooling and equipment components are excluded. Mid-year moves and previously advanced nominal payments are not separately tracked."

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.otda.heap.payment
        tier_one = spm_unit("ny_heap_tier_one", period)
        fuel = spm_unit("heating_type", period)
        base = p.base[fuel]
        direct = where(
            base > 0,
            base
            + tier_one * p.tier_one_supplement
            + spm_unit("ny_heap_vulnerable", period) * p.vulnerable_supplement,
            0,
        )
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        dwelling = spm_unit("ny_heap_dwelling_type", period)
        group = dwelling == dwelling.possible_values.ELIGIBLE_GROUP_RESIDENCE
        heat_included = where(
            subsidized | group,
            p.heat_included.nominal,
            where(tier_one, p.heat_included.tier_one, p.heat_included.tier_two),
        )
        return where(
            spm_unit("heat_expense_included_in_rent", period) | group,
            heat_included,
            direct,
        )
