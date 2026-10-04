from policyengine_us.model_api import *


class ia_liheap_has_energy_burden(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Iowa LIHEAP household has an energy burden"
    documentation = (
        "Section 5.50: 'the household must have an energy burden on the date of "
        "application', meaning it 'must be vulnerable to increases in energy "
        "costs'. True when the household pays a vendor for its heating fuel, "
        "when heat is included in unsubsidized rent, or when heat is included "
        "in subsidized rent and the household has its own electric account, "
        "proxied by a positive pre-subsidy electricity expense. Direct-pay "
        "routing, landlord bill shares, disconnect notices and the 'not charged "
        "by anyone' case of Appendix D are not identified by existing inputs."
    )
    reference = (
        # Section 5.41-5.42 (pages 20-21), Section 5.50 (page 22) and Appendix
        # D, Energy Burden Table (pages 122-123).
        "https://hhs.iowa.gov/media/17262/download?inline#page=122",
        # Section 2.3, subsidized housing and utilities-in-rent policies.
        "https://liheapch.acf.gov/docs/2026/state-plans/IA_Plan_2026.pdf#page=8",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        # Appendix D: "The LIHEAP customer pays a vendor directly for utilities"
        # has an energy burden.
        pays_for_heat = spm_unit("has_heating_expense", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        # Definitions, Subsidized Housing: assistance "provided by a government
        # agency or a non-profit program", including Section 8, TBRA, Section
        # 202, public housing, VASH and income-restricted apartments.
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        # Section 5.41: "Non-subsidized households where all energy utilities
        # are included in the rent are eligible for LIHEAP Regular Assistance
        # because the benefit amount is determined by a matrix". "Subsidized
        # households where heat is included in the rent are eligible ...
        # provided they have a secondary energy burden with a utility vendor";
        # those "where both heat and electric are included in the rent are
        # ineligible". Appendix D requires the household to be "billed directly
        # for electric"; a positive electricity bill is the proxy.
        has_electric_account = spm_unit("pre_subsidy_electricity_expense", period) > 0
        heat_in_rent_eligible = heat_in_rent & (~subsidized | has_electric_account)
        return pays_for_heat | heat_in_rent_eligible
