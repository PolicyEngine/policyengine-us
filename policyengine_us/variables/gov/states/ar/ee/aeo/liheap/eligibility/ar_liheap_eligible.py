from policyengine_us.model_api import *


class ar_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Arkansas LIHEAP regular heating assistance"
    defined_for = StateCode.AR
    # Plan sections 1.5 and 2.1-2.3, pages 5 and 9-10: no categorical
    # income bypass or asset test; direct or indirect heating burden required.
    reference = "https://liheapch.acf.gov/docs/2026/state-plans/AR_Plan_2026.pdf#page=9"

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
        # For direct bills, reported heating costs are assumed to represent
        # the household's remaining obligation after any utility allowance,
        # not a gross bill already fully reimbursed. Verification is not modeled.
        direct_responsibility = (expense > 0) | has_expense
        heating_responsibility = where(
            heat_in_rent, rent_responsibility, direct_responsibility
        )
        return (
            (size > 0)
            & (income <= income_limit)
            & (fuel != fuel.possible_values.NONE)
            & heating_responsibility
        )
