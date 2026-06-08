from policyengine_us.model_api import *


class fl_sr_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Florida School Readiness family copay"
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = (
        "https://www.elclc.org/wp-content/uploads/2025/10/2025-2026-Sliding-Fee-Schedule-for-10012025-4-and-6-Percent.pdf#page=1",
        "https://www.elcduval.org/wp-content/uploads/2025/07/Rule-6M-4.400_Frequently-Asked-Questions.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl["del"].sr.copay
        countable_income = spm_unit("fl_sr_countable_income", period)
        monthly_smi = spm_unit("fl_sr_smi", period)
        smi_ratio = where(monthly_smi > 0, countable_income / monthly_smi, 0)

        # One copay per household (6M-4.400 FAQ Q7/Q13). Full-time copay
        # percentages apply when any eligible child has full-time authorized
        # care; otherwise the part-time percentages apply.
        person = spm_unit.members
        is_eligible_child = person("is_fl_sr_child_eligible", period)
        time_category = person("fl_sr_time_category", period)
        is_full_time = time_category == time_category.possible_values.FULL_TIME
        any_full_time = spm_unit.sum(is_eligible_child & is_full_time) > 0

        copay_rate = where(
            any_full_time,
            p.smi_scale.full_time_rate.calc(smi_ratio),
            p.smi_scale.part_time_rate.calc(smi_ratio),
        )
        copay = countable_income * copay_rate
        # The copay may not exceed 7% of family income (45 CFR 98.45(l)(3)).
        return min_(copay, countable_income * p.max_share_of_income)
