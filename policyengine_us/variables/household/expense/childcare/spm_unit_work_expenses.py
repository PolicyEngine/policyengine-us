from policyengine_us.model_api import *


class spm_unit_work_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit work expenses"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        weeks_worked = person("weeks_worked", period)
        is_adult = person("is_adult", period)
        earned_income = person("earned_income", period)
        weekly_amount = parameters(period).gov.census.spm.work_expense.weekly_amount

        eligible_weeks = is_adult * (earned_income > 0) * np.clip(
            weeks_worked, 0, 52
        )
        return spm_unit.sum(eligible_weeks) * weekly_amount
