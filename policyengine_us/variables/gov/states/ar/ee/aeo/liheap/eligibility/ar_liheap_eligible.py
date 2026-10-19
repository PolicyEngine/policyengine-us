from policyengine_us.model_api import *


class ar_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Arkansas LIHEAP regular heating assistance"
    defined_for = StateCode.AR
    # Plan question 1.4 and sections 2.1-2.3: no categorical income bypass or
    # asset test; direct or indirect heating burden required.
    # PDF pages 5, 9-10
    reference = "https://liheapch.acf.gov/docs/2026/state-plans/AR_Plan_2026.pdf#page=5"

    def formula(spm_unit, period, parameters):
        size = spm_unit("ar_liheap_household_size", period)
        income = spm_unit("ar_liheap_countable_income", period)
        income_limit = spm_unit("ar_liheap_income_limit", period)
        fuel = spm_unit("heating_type", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        expense = spm_unit("heating_expense", period)
        has_expense = spm_unit("has_heating_expense", period)
        subsidized = spm_unit.household("is_in_public_housing", period) | spm_unit(
            "receives_housing_assistance", period
        )
        # For subsidized heat included in rent, a positive expense represents
        # a verified excess charge. The general responsibility flag cannot
        # substitute for this surcharge. Unsubsidized rent needs no extra bill.
        rent_responsibility = ~subsidized | (expense > 0)
        # A direct bill or obligation counts through has_heating_expense, which
        # defaults to a positive primary-fuel bill with heat not in rent. An
        # explicit false (for example, a bill fully reimbursed through a utility
        # allowance, FY2026 plan item 2.3, page 10) is respected. Verification
        # is not modeled.
        heating_responsibility = where(heat_in_rent, rent_responsibility, has_expense)
        return (
            (size > 0)
            & (income <= income_limit)
            & (fuel != fuel.possible_values.NONE)
            & heating_responsibility
        )
