from policyengine_us.model_api import *


class nm_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "New Mexico LIHEAP regular heating eligibility"
    defined_for = StateCode.NM
    reference = (
        # 8.150.410.8, 8.150.410.9, 8.150.410.11, 8.150.410.13 and
        # 8.150.410.14 NMAC
        "https://www.srca.nm.gov/parts/title08/08.150.0410.html",
        # 8.150.100.9 C-E NMAC
        "https://www.srca.nm.gov/parts/title08/08.150.0100.html",
        # 8.150.510.8 NMAC
        "https://www.srca.nm.gov/parts/title08/08.150.0510.html",
        # 8.150.520.14 NMAC
        "https://www.srca.nm.gov/parts/title08/08.150.0520.html",
        "https://liheapch.acf.gov/docs/2026/state-plans/NM_Plan_2026.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("nm_liheap_household_size", period)
        income = spm_unit("nm_liheap_countable_income", period)
        limit = spm_unit("nm_liheap_income_limit", period)
        # Annual income against 12 times the monthly limit stands in for the
        # 30-day gross income test. No household is categorically eligible
        # and no asset test applies. The 150% limit exceeds the 110% floor of
        # 42 U.S.C. 8624(b)(2)(B) for every size, so the floor never binds.
        income_eligible = income <= limit
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        # A home without heat has no heating cost. An unspecified fuel
        # qualifies only when heat is included in the rent.
        fuel_qualifies = (heating_type != types.NONE) & (
            heat_in_rent | (heating_type != types.UNSPECIFIED)
        )
        # Heat included in unsubsidized rent qualifies even when no utility
        # cost is designated. Subsidized tenants whose heat is included in the
        # rent qualify only with an additional out-of-pocket heating cost.
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        out_of_pocket = spm_unit("heating_expense", period) > 0
        rent_responsible = ~subsidized | out_of_pocket
        # Households that heat with wood they gather themselves have a heating
        # responsibility without a bill.
        wood = heating_type == types.WOOD
        direct_responsible = spm_unit("has_heating_expense", period) | wood
        responsible = where(heat_in_rent, rent_responsible, direct_responsible)
        return (size > 0) & income_eligible & fuel_qualifies & responsible
