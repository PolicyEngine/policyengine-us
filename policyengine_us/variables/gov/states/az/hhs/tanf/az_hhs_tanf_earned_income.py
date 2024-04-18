from policyengine_us.model_api import *


class az_tanf_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Earned income for the Arizona Cash Assistance"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        # Earned income of the spm unit
        income = add(spm_unit, period, ["earned_income"])
        # Determine the expense discount
        p = parameters(period).gov.states.az.hhs.tanf.eligibility.income.earned
        # Yearly subtracted income disregard
        yearly_flat_discount = p.flat * MONTHS_IN_YEAR
        # Income after subtracting constant value and certain percentage
        income_after_flat_disregard = max_(income - yearly_flat_discount, 0)
        income_percentage_disregard = income_after_flat_disregard * (1 - p.percentage)
        # Calculate countable earned income by further subtracting earned income disregard
        earned_income_care_expense_disregard = spm_unit(
            "az_hhs_tanf_earned_income_care_expense_disregard", period
        )
        return max_(income_percentage_disregard - earned_income_care_expense_disregard, 0)
