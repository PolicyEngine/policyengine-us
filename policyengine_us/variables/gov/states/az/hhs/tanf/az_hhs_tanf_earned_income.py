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
        # Get the age of the child(children) and the disabled adult(s)
        person = spm_unit.members
        member_age = person("age" , period)
        # Get the childcare and disabled adult care expenses
        special_care_expense = spm_unit("care_expenses", period)
        # Monthly care expense
        monthly_care_expense = special_care_expense/MONTHS_IN_YEAR
        initially_discounted_income = income - p.flat
        # Determine the expense discount
        p = parameters(period).gov.states.az.hhs.tanf.eligibility.income.earned
        
        # Whether the kid is under the age threshold with higher income calculation discount
        # Determine the disabled adult care expense after discount
        adult_discount_threshold=where(member_age > 18, p.adult , 0)
        capped_adult_expense_disregard = min_(spm_unit.sum(monthly_care_expense), adult_discount_threshold)        

        # Calculate capped disabled adult care expense
        # use age eligibility variable later
        eligible_child = person("az_tanf_eligible_child",period)
        whether_young_child = member_age < p.child_age
        uncapped_child_expnese_disregard = eligible_child * monthly_care_expense
        child_discount_threshold = where(whether_young_child, p.younger, p.older)
        capped_child_expense_disregard = min_(spm_unit.sum(uncapped_child_expnese_disregard), child_discount_threshold)
        return  initially_discounted_income * p.percentage - capped_child_expense_disregard - capped_adult_expense_disregard
