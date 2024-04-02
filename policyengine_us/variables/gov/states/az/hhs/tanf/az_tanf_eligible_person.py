from policyengine_us.model_api import *

class az_tanf_(Variable):
    value_type = float
    entity = SPMUnit
    label = ""
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        # Earned income of the spm unit
        income = add(spm_unit, period, ["earned_income"])
        # Childcare expenses
        childcare = spm_unit("childcare_expenses", period)
         # Get the age of the child
        child_age = spm_unit("age" , period)
        # Disabled adult expenses
        disabled_adult_care = spm_unit("care_expenses", period)
        # Determine the expense discount
        p = parameters(period).gov.states.az.hhs.tanf.eligibility.income.earned
        childcare_expense_discount= min_(where(child_age<p.child_age, p.younger, p.older),childcare)
        # Determine the disabled adult care expense after discount
        disabled_care_expense_discount=min_(disabled_adult_care,p.adult)
        return (income-p.flat)*p.percentage-childcare_expense_discount-disabled_care_expense_discount