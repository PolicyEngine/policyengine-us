from policyengine_us.model_api import *


class az_hhs_tanf_earned_income_care_expense_disregard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona Cash Assistance care expense earned income disregard"
    definition_period = MONTH
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.hhs.tanf.eligibility.income.earned.care_expenses
        # Get the age of the child(children) and the disabled adult(s)
        person = spm_unit.members
        age = person("age", period) * MONTHS_IN_YEAR
        # Get the childcare and disabled adult care expenses
        care_expenses = add(
            spm_unit, period, ["childcare_expenses", "care_expenses"]
        )
        # Determine the total eligible disregard
        # The eligibility reuquirements consider whether children or disabled adults
        is_child = person("az_tanf_eligible_child", period)
        child = person("is_child", period)
        disabled_adult = person("is_disabled", period) & ~child
        # Calculate eligible child disregard
        child_amount = p.child_amounts.calc(age) * is_child
        # Calculate eligible disabled adult disregard
        adult_amount = disabled_adult * p.adult
        total_amount = spm_unit.sum(child_amount + adult_amount)
        # The disregard is capped at the expenses
        return min_(care_expenses, total_amount)
