from policyengine_us.model_api import *


class oh_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Ohio HEAP eligibility"
    defined_for = StateCode.OH
    reference = (
        "https://www.clevelandohio.gov/sites/clevelandohio/files/aging/Home%20repair%20Applications/2025-2026_HEAP_application_B_W.pdf#page=1",
        "https://dam.assets.ohio.gov/image/upload/v1769700600/development.ohio.gov/individual/energyassistance/DETAILED_MODEL_PLAN_LIHEAP__10_01_2025.pdf#page=8",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("oh_liheap_household_size", period)
        income = spm_unit("oh_liheap_countable_income", period)
        limit = spm_unit("oh_liheap_income_limit", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        # A primary heating bill approximates the verified household liability,
        # including the household's own portion in subsidized housing. For
        # nonsubsidized heat in rent, the flag represents the verified arrangement.
        responsible = (spm_unit("heating_expense", period) > 0) | (
            heat_in_rent & ~subsidized
        )
        heating_type = spm_unit("heating_type", period)
        fuel = heating_type.possible_values
        # No categorical income bypass or asset test. Existing inputs cannot
        # identify every excluded institution, boarding house, or legal fixture.
        return (
            (size > 0) & (income <= limit) & responsible & (heating_type != fuel.NONE)
        )
