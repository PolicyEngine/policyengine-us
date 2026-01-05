from policyengine_us.model_api import *


class nh_fanf_child_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Hampshire FANF child/dependent care deduction"
    unit = USD
    definition_period = MONTH
    reference = "https://www.dhhs.nh.gov/famar_htm/index.htm#html/603_05_child_dependent_care_deduction_sr_12-04_07_12_fam_a.htm"
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.nh.dhhs.fanf.income.child_care_deduction
        person = spm_unit.members

        # Determine if any earner is full-time (≥$377/month)
        earned_income = person("tanf_gross_earned_income", period)
        is_full_time = earned_income >= p.full_time_threshold
        any_full_time = spm_unit.any(is_full_time)

        # Get child age and status
        age = person("age", period.this_year)
        is_child = person("is_child", period)

        # Calculate max deduction per child based on employment status and age
        full_time_max = p.full_time.calc(age)
        part_time_max = p.part_time.calc(age)
        max_per_child = where(any_full_time, full_time_max, part_time_max)

        # Only count children
        max_deduction_per_child = max_per_child * is_child
        total_max_deduction = spm_unit.sum(max_deduction_per_child)

        # Cap at actual childcare expenses
        childcare_expenses = spm_unit("childcare_expenses", period)

        return min_(childcare_expenses, total_max_deduction)
