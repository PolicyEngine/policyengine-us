from policyengine_us.model_api import *


class ri_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Rhode Island LIHEAP regular heating eligibility"
    defined_for = StateCode.RI
    reference = (
        # PDF pages 5-6, 12
        "https://ripuc.ri.gov/eventsactions/docket/4290-DHS-DR-PUC%203-6%20attachment%20LIHEAP%20Manual%202020%20-%20Final.pdf#page=5",
        "https://liheapch.acf.gov/docs/2026/state-plans/RI_Plan_2026.pdf#page=8",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("ri_liheap_household_size", period)
        income = spm_unit("ri_liheap_income", period)
        limit = spm_unit("ri_liheap_income_limit", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        primary_obligation = spm_unit("has_heating_expense", period) | (
            spm_unit("heating_expense", period) > 0
        )
        separate_electric_bill = spm_unit("pre_subsidy_electricity_expense", period) > 0
        # Reported obligations and rental terms are assumed verified. A utility
        # burden permits subsidized heat-in-rent eligibility, but does not select
        # the direct versus secondary-electric payment route.
        energy_burden = primary_obligation | (
            heat_in_rent & (~subsidized | separate_electric_bill)
        )
        heating_type = spm_unit("heating_type", period)
        return (
            (size > 0)
            & (income <= limit)
            & energy_burden
            & (heating_type != heating_type.possible_values.NONE)
        )
