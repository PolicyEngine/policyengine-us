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
        age = person("age", period)
        # Get the childcare and disabled adult care expenses
        care_expenses = spm_unit("childcare_expenses", period)

        # Determine the total eligible disregard
        # The eligibility reuquirements consider wither children or disabled adults
        young_eligible_child = age < p.child_age
        is_child = person("is_child", period)
        disabled = person("is_disabled", period)
        old_eligible_dependent = is_child | disabled
        disregard_amount = select(
            [
                young_eligible_child,
                old_eligible_dependent,
            ],
            [
                p.younger,
                p.older,
            ],
            default=0,
        )
        total_disregard = spm_unit.sum(disregard_amount)

        # The disregard is capped at the expenses

        capped_disregard = min_(care_expenses, total_disregard)

        # Monthly care expense
        monthly_care_expense = special_care_expense / MONTHS_IN_YEAR
        initially_discounted_income = income - p.flat
        # Determine the expense discount
        p = parameters(period).gov.states.az.hhs.tanf.eligibility.income.earned

        # Whether the kid is under the age threshold with higher income calculation discount
        # Determine the disabled adult care expense after discount
        adult_monthy_care_expense = where(age > 18, monthly_care_expense, 0)
        adult_discount_threshold = p.adult
        capped_adult_expense_disregard = min_(
            spm_unit.sum(adult_monthy_care_expense), adult_discount_threshold
        )

        # Calculate capped disabled adult care expense
        # use age eligibility variable later
        eligible_child = person("az_tanf_eligible_child", period)
        uncapped_child_expense_disregard = (
            eligible_child * monthly_care_expense
        )
        capped_child_expense_disregard = min_(
            spm_unit.sum(uncapped_child_expense_disregard),
            child_discount_threshold,
        )
        monthly_discounted_earned_income = (
            initially_discounted_income * p.percentage
            - capped_child_expense_disregard
            - capped_adult_expense_disregard
        )
        yearly_discounted_earned_income = monthly_discounted_earned_income * 12
        return yearly_discounted_earned_income
