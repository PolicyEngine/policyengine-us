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
        person = spm_unit.members
        age = person("age", period)
        # Determine the expense discount
        p = parameters(period).gov.states.az.hhs.tanf.eligibility.income.earned
        # Income after subtracting constant value and certain percentage
        after_subtracted_income = income - p.flat * MONTHS_IN_YEAR
        after_discounted_income = after_subtracted_income * (1 - p.percentage)
        #Calculate countable earned income by further subtracting earned income disregard 
        countable_earned_income = max(after_discounted_income - 'az_hhs_tanf_earned_income_disregard',0)
        return countable_earned_income
