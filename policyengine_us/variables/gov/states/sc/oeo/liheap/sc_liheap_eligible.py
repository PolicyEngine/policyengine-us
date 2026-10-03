from policyengine_us.model_api import *


class sc_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for South Carolina LIHEAP regular heating assistance"
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20LIHEAP%20State%20Plan.pdf#page=8,9",
        "https://oeo.sc.gov/managedsites/prd/oeo/liheap.html",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("sc_liheap_household_size", period)
        income = spm_unit("sc_liheap_countable_income", period)
        limit = spm_unit("sc_liheap_income_limit", period)
        fuel = spm_unit("heating_type", period)
        heating_responsibility = spm_unit("has_heating_expense", period) | spm_unit(
            "heat_expense_included_in_rent", period
        )
        return (
            (size > 0)
            & (income <= limit)
            & (fuel != fuel.possible_values.NONE)
            & heating_responsibility
        )
