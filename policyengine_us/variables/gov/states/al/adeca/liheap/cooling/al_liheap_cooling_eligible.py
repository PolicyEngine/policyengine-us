from policyengine_us.model_api import *


class al_liheap_cooling_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Alabama LIHEAP regular cooling assistance eligibility"
    defined_for = StateCode.AL
    reference = (
        # PDF pages 9, 16-17, 21-22
        "https://adeca.alabama.gov/wp-content/uploads/FY-2026-LIHEAP-Manual-1.pdf#page=9",
        "https://liheapch.acf.gov/docs/2026/state-plans/AL_Plan_2026.pdf#page=11",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("al_liheap_household_size", period)
        income = spm_unit("al_liheap_countable_income", period)
        limit = spm_unit("al_liheap_cooling_income_limit", period)
        # The cooling cost input stands for the recent cooling bill (manual
        # 5.3) and, for subsidized tenants, the out-of-pocket energy cost that
        # manual 6.1.1 requires. Renters in nonsubsidized housing whose energy
        # costs are included in the rent are also eligible (manual 5.3 and
        # 6.1.3).
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        # Heating's rent route reads heat_expense_included_in_rent instead, so a
        # renter with energy costs in the rent also sets tenant_pays_utilities
        # to false for this route.
        utilities_in_rent = ~spm_unit.household("tenant_pays_utilities", period) & (
            add(spm_unit, period, ["rent"]) > 0
        )
        responsible = spm_unit("has_cooling_expense", period) | (
            utilities_in_rent & ~subsidized
        )
        # Cooling pays the Electric column whatever the heating fuel, so
        # heating_type, including UNSPECIFIED, does not affect eligibility.
        return (size > 0) & (income <= limit) & responsible
