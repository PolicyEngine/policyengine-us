from policyengine_us.model_api import *


class hi_tanf_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii TANF dependent care deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        # HAR 17-676-54.1(c)(4) and (d)(4), PDF pages 36-37
        "https://humanservices.hawaii.gov/wp-content/uploads/2019/03/HAR-17-676-INCOME.pdf#page=36",
        "https://humanservices.hawaii.gov/wp-content/uploads/2024/12/Hawaii_TANF_State_Plan_Signed_Certified-Eff_20231001.pdf#page=20",
    )
    defined_for = StateCode.HI

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.dhs.tanf.deductions.dependent_care
        # HAR 17-676-54.1(c)(4) and (d)(4) deduct "the actual cost for the
        # care of each incapacitated adult living in the same household and
        # receiving financial assistance", up to $175 a month if the
        # applicant is employed full time or $165 if less than full time.
        # The rule covers incapacitated adults only; child care costs are
        # not deducted here.
        person = spm_unit.members
        is_adult = ~person("is_child", period.this_year)
        care_cost = is_adult * person(
            "hi_tanf_qualifying_incapacitated_adult_care_expenses", period
        )
        # The cap follows the working applicant's employment: full time is
        # 32 or more hours a week (HAR 17-676-2). When several adults work,
        # the applicant is treated as full time if any of them is.
        hours = person("weekly_hours_worked_before_lsr", period.this_year)
        max_adult_hours = spm_unit.max(where(is_adult, hours, 0))
        cap = spm_unit.project(p.amount.calc(max_adult_hours))
        # Each adult's cost is capped separately.
        return spm_unit.sum(min_(care_cost, cap))
