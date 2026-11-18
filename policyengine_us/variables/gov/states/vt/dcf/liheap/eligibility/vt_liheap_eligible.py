from policyengine_us.model_api import *


class vt_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Vermont LIHEAP regular heating eligibility"
    defined_for = StateCode.VT
    reference = (
        # PDF pages 10, 16, 38, 43
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2900-Seasonal-Fuel-Assistance.pdf#page=10",
        "https://legislature.vermont.gov/statutes/section/33/026/02604",
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/ESD-Procedure-P2916.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("vt_liheap_household_size", period)
        income = spm_unit("vt_liheap_income", period)
        limit = spm_unit("vt_liheap_income_limit", period)
        heating_cost = spm_unit("vt_liheap_heating_cost", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        # Rule 2916(b) requires a primary heating fuel listed in the standard
        # heating cost tables. The $21 benefit for subsidized heat in rent needs
        # no known fuel, but NONE means the home has no heating, so it is
        # ineligible in every case. A listed fuel without heat in rent is treated
        # as paid to the supplier directly; the benefit uses the standard cost,
        # not a bill.
        heating_type = spm_unit("heating_type", period)
        has_heat = heating_type != heating_type.possible_values.NONE
        has_heating_cost = (heating_cost > 0) | (heat_in_rent & subsidized)
        return (size > 0) & (income <= limit) & has_heat & has_heating_cost
