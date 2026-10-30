from policyengine_us.model_api import *


class nd_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for North Dakota LIHEAP regular heating assistance"
    reference = (
        "https://www.nd.gov/dhs/policymanuals/415/415_20_10.htm",
        "https://www.nd.gov/dhs/policymanuals/415/415_20_10_30.htm",
        "https://www.nd.gov/dhs/policymanuals/415/415_20_10_50.htm",
    )
    defined_for = StateCode.ND

    def formula(spm_unit, period, parameters):
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        responsibility = heat_in_rent | (spm_unit("heating_expense", period) > 0)
        # Manual 415-20-10: "Tenants of subsidized housing in which heat is
        # included in the rent are not eligible. If a subsidized household has
        # heat or electricity included in their rent, but they have the
        # opposite (heat or electricity) bill in their name, the household is
        # eligible for only the heat or electric bill in their name."
        # As in every state, an UNSPECIFIED heating_type is a missing input that
        # pays nothing, so the electric-bill path needs a known heating_type.
        own_electric_bill = (
            spm_unit("pre_subsidy_electricity_expense", period) > 0
        ) & (heating_type != types.UNSPECIFIED)
        housing_eligible = ~(heat_in_rent & subsidized) | own_electric_bill
        # Residence is approximated by state/SPMUnit membership. Institutional,
        # transient-residence and tribal election/duplicate-aid facts are not
        # available; households are assumed to use the state program.
        return (
            (spm_unit("nd_liheap_household_size", period) > 0)
            & (spm_unit("nd_liheap_share", period) > 0)
            & (heating_type != types.NONE)
            & responsibility
            & housing_eligible
        )
