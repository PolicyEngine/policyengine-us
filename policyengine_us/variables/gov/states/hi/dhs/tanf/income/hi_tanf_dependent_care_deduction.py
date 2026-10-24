from policyengine_us.model_api import *


class hi_tanf_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii TANF dependent care deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/hawaii/Haw-Code-R-SS-17-676-54-1",
        "https://www.law.cornell.edu/regulations/hawaii/Haw-Code-R-SS-17-676-2",
        "https://humanservices.hawaii.gov/wp-content/uploads/2024/12/Hawaii_TANF_State_Plan_Signed_Certified-Eff_20231001.pdf#page=20",
    )
    defined_for = StateCode.HI

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.dhs.tanf.deductions.dependent_care

        # Per HAR 17-676-54.1(c)(4) and (d)(4) and the HAR 17-676-2
        # definition, the deduction covers only the cost of care for each
        # incapacitated adult in the household (State Plan section 10.2.1(D):
        # a disabled adult household member). Child care is not deducted.
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])

        # Count disabled adults in the unit for the per-person cap
        person = spm_unit.members
        is_adult = ~person("is_child", period.this_year)
        is_disabled_adult = is_adult & person("is_disabled", period.this_year)
        num_care_recipients = spm_unit.sum(is_disabled_adult)

        # Determine rate based on MAX of adult hours
        # If either parent works full-time, use full-time rate
        hours = person("weekly_hours_worked_before_lsr", period.this_year)
        # Only consider adult hours (children get 0)
        adult_hours = where(is_adult, hours, 0)
        max_adult_hours = spm_unit.max(adult_hours)

        # Full-time = 32+ hours/week
        # Rate is $175 (full-time) or $165 (part-time) per person
        rate = p.amount.calc(max_adult_hours)
        max_deduction = num_care_recipients * rate

        # Deduct actual cost up to max per care recipient
        return min_(adult_care_expenses, max_deduction)
