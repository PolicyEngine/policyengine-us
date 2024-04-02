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
        # Childcare expenses
        childcare = spm_unit("childcare_expenses", period)
        # Get the age of the child
        person = spm_unit.members
        child_age = person("age" , period)
        # Disabled adult expenses
        disabled_adult_care = spm_unit("care_expenses", period)
        # Determine the expense discount
        p = parameters(period).gov.states.az.hhs.tanf.eligibility.income.earned
        young_child = child_age < p.child_age
        uncapped_expense_disregard = spm_unit.sum(where(young_child, p.younger, p.older))
        capped_expense_disregard = min_(uncapped_expense_disregard, childcare)
        # Determine the disabled adult care expense after discount
        disabled_care_expense_discount = min_(disabled_adult_care, p.adult)
        return (income - p.flat) * p.percentage - capped_expense_disregard - disabled_care_expense_discount
