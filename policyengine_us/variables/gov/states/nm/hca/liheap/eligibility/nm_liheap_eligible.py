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
        # heating_type is a required input and an unspecified fuel qualifies
        # only when heat is included in the rent. A home without heating
        # stays eligible: the energy cost may be a cooling cost, and the one
        # regular benefit pays a heating or cooling bill the household picks.
        known_fuel = heat_in_rent | (heating_type != types.UNSPECIFIED)
        # A heating fuel or electric bill is an energy cost, including the
        # additional out-of-pocket cost of a subsidized tenant whose heat is
        # included in the rent. Electricity used only for lighting has no
        # separate input.
        has_energy_bill = (spm_unit("heating_expense", period) > 0) | (
            spm_unit("pre_subsidy_electricity_expense", period) > 0
        )
        # Without a bill, heat included in unsubsidized rent qualifies, and
        # households that heat with wood they gather themselves have a heating
        # responsibility.
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        responsible = has_energy_bill | where(
            heat_in_rent, ~subsidized, heating_type == types.WOOD
        )
        return (size > 0) & income_eligible & known_fuel & responsible
