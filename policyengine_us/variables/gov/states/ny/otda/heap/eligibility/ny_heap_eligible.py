from policyengine_us.model_api import *


class ny_heap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP regular heating eligibility"
    defined_for = StateCode.NY
    reference = (
        # PDF pages 34, 37, 44, 45, 46, 47, 48.
        "https://otda.ny.gov/programs/heap/HEAP-manual.pdf#page=34",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-393.4",
    )
    documentation = (
        "Regular heating has no resource test. SPM units approximate energy-sharing "
        "households. Application timing, SSN documentation, duplicate payments and the "
        "full set of excluded member categories are not modeled."
    )

    def formula(spm_unit, period, parameters):
        dwelling = spm_unit("ny_heap_dwelling_type", period)
        types = dwelling.possible_values
        heat = (
            spm_unit("has_heating_expense", period)
            | spm_unit("heat_expense_included_in_rent", period)
            | (dwelling == types.ELIGIBLE_GROUP_RESIDENCE)
        )
        income_eligible = spm_unit("ny_heap_categorically_eligible", period) | (
            spm_unit("ny_heap_countable_income", period)
            <= spm_unit("ny_heap_income_limit", period)
        )
        return (
            heat
            & income_eligible
            & (spm_unit("ny_heap_household_size", period) > 0)
            & (dwelling != types.INELIGIBLE_RESIDENCE)
        )
