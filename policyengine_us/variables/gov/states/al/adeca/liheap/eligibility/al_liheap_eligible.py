from policyengine_us.model_api import *


class al_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Alabama LIHEAP eligibility"
    defined_for = StateCode.AL
    # PDF pages 13, 21-22
    reference = "https://adeca.alabama.gov/wp-content/uploads/FY-2026-LIHEAP-Manual-1.pdf#page=13"

    def formula(spm_unit, period, parameters):
        size = spm_unit("al_liheap_household_size", period)
        income = spm_unit("al_liheap_countable_income", period)
        limit = spm_unit("al_liheap_income_limit", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        pays_for_heat = spm_unit("heating_expense", period) > 0
        # Heat included in nonsubsidized rent can qualify without a separate
        # bill. The rent flag stands for the agency's verified arrangement.
        # In subsidized housing, a positive heating bill approximates verified
        # excess charges; the input does not distinguish the excess component.
        responsible = pays_for_heat | (heat_in_rent & ~subsidized)
        heating_type = spm_unit("heating_type", period)
        fuel = heating_type.possible_values
        return (
            (size > 0) & (income <= limit) & responsible & (heating_type != fuel.NONE)
        )
