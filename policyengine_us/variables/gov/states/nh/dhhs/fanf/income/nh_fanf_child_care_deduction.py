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
        p = parameters(period).gov.states.nh.dhhs.fanf.income.child_care_deduction
        person = spm_unit.members

        # Determine if any earner is full-time (≥$377/month)
        earned_income = person("tanf_gross_earned_income", period)
        is_full_time = earned_income >= p.full_time_threshold
        any_full_time = spm_unit.any(is_full_time)

        # Get child age and status
        age = person("age", period.this_year)
        is_child = person("is_child", period)
        # Per FAM 603.05, the deduction also covers an incapacitated parent
        # living in the employed person's home, at the age-2+ tier.
        incapacitated_parent = person("is_tax_unit_head_or_spouse", period) & person(
            "is_incapable_of_self_care", period.this_year
        )

        # Calculate max deduction per person based on employment status and age
        full_time_max = p.full_time.calc(age)
        part_time_max = p.part_time.calc(age)
        any_full_time_person = spm_unit.project(any_full_time)
        max_per_person = where(any_full_time_person, full_time_max, part_time_max)

        # Count children and incapacitated parents
        care_recipient = is_child | incapacitated_parent
        max_deduction_per_person = max_per_person * care_recipient
        total_max_deduction = spm_unit.sum(max_deduction_per_person)

        # Cap at actual care expenses.
        childcare_expenses = spm_unit("childcare_expenses", period)
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])

        return min_(childcare_expenses + adult_care_expenses, total_max_deduction)
