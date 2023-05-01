from policyengine_us.model_api import *


class nj_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Jersey TANF countable earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # Get gross earned income.
        gross_earned_income = spm_unit("nj_tanf_gross_earned_income", period)
        p = parameters(
            period
        ).gov.states.nj.njdhs.tanf.income.earned_income_deduction
        months_enrolled_in_tanf = person("months_enrolled_in_tanf", period)
        weekly_hours_worked = person("weekly_hours_worked", period)
        # New Jerset Admin Code 10:90-3.8(b)
        return where(
            months_enrolled_in_tanf > 1,
            where(
                months_enrolled_in_tanf > 7,
                gross_earned_income * (1 - p.additional_percent),
                where(
                    weekly_hours_worked >= p.work_hours_threshold,
                    gross_earned_income * (1 - p.consecutive_month_percent),
                    gross_earned_income * (1 - p.additional_percent),
                ),
            ),
            gross_earned_income * (1 - p.first_month_percent),
        )
