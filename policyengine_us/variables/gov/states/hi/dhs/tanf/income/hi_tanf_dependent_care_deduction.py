from policyengine_us.model_api import *


class hi_tanf_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii TANF dependent care deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://humanservices.hawaii.gov/wp-content/uploads/2024/12/Hawaii_TANF_State_Plan_Signed_Certified-Eff_20231001.pdf#page=20",
    )
    defined_for = StateCode.HI

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.dhs.tanf.deductions.dependent_care

        # Get actual childcare expenses (YEAR variable, auto-converts to monthly)
        expenses = spm_unit("childcare_expenses", period)

        # Count children in the unit for the per-child cap
        person = spm_unit.members
        is_child = person("is_child", period.this_year)
        num_children = spm_unit.sum(is_child)

        # Determine rate based on MAX of adult hours
        # If either parent works full-time, use full-time rate
        is_adult = ~person("is_child", period.this_year)
        hours = person("weekly_hours_worked_before_lsr", period.this_year)
        # Only consider adult hours (children get 0)
        adult_hours = where(is_adult, hours, 0)
        max_adult_hours = spm_unit.max(adult_hours)

        # Full-time = 32+ hours/week
        # Rate is $175 (full-time) or $165 (part-time) per child
        rate = p.amount.calc(max_adult_hours)
        max_deduction = num_children * rate

        # Deduct actual cost up to max per child
        return min_(expenses, max_deduction)
