from policyengine_us.model_api import *


class wa_wccc_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Activity eligible for Washington WCCC"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0005",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0020",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0040",
        "https://app.leg.wa.gov/RCW/default.aspx?cite=43.216.814",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # Self-employment activity counts regardless of profitability, so any
        # non-zero self-employment income qualifies (positive or a loss).
        employment_income = person("employment_income", period.this_year)
        self_employment_income = person("self_employment_income", period.this_year)
        has_work_activity = (employment_income > 0) | (self_employment_income != 0)
        is_student = person("is_full_time_student", period.this_year)
        # WAC 110-15-0040 and RCW 43.216.814(1) qualify K-12 attendance as an
        # approved activity for teen parents. WAC 110-15-0020(2)(b) waives the
        # approved-activity requirement for parents who are medically
        # incapacitated. We don't track approved-activity hours at the moment;
        # treat any earnings, self-employment activity, full-time student
        # status, K-12 attendance, or disability as meeting the activity test.
        is_in_k12 = person("is_in_k12_school", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        individually_eligible = has_work_activity | is_student | is_in_k12 | is_disabled
        return spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
