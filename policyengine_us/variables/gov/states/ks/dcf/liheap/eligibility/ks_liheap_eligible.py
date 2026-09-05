from policyengine_us.model_api import *


class ks_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Kansas LIEAP"
    documentation = "Kansas household that is income eligible, has at least one U.S. citizen or qualified alien member, heats its home (energy vulnerability), and is not a subsidized-housing renter whose heating costs are included in the rent."
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/current/keesm13300.htm",
        "https://liheapch.acf.gov/docs/2026/state-plans/KS_Plan_2026.pdf#page=8",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("ks_liheap_income_eligible", period)
        has_citizen = spm_unit("ks_liheap_household_size", period) > 0
        heating_type = spm_unit("heating_type", period)
        has_heating = heating_type != heating_type.possible_values.NONE
        housing_assistance = spm_unit("receives_housing_assistance", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized_heat_in_rent = housing_assistance & heat_in_rent
        return income_eligible & has_citizen & has_heating & ~subsidized_heat_in_rent
