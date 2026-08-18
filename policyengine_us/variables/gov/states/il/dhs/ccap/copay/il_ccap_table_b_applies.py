from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.il.dhs.ccap.rates.il_ccap_care_duration import (
    ILCCAPCareDuration,
)


class il_ccap_table_b_applies(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Illinois CCAP Table B copayment applies"
    documentation = "Whether the family copayment is assessed under Table B, which applies from September through May when every child in care is school age and approved for part-day care."
    defined_for = StateCode.IL
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=54862",
        "https://www.dhs.state.il.us/OneNetLibrary/27897/documents/Forms/443455B%20CCAP%20Income%20and%20Copay%20Chart%20Eff%207.1.25.pdf#page=5",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap.copay.table_b
        # The school-year window wraps the calendar year end, running from
        # September through May.
        month = period.start.month
        in_school_year = (month >= p.start_month) | (month <= p.end_month)
        person = spm_unit.members
        eligible_child = person("il_ccap_eligible_child", period)
        duration = person("il_ccap_care_duration", period)
        in_care = eligible_child & (duration != ILCCAPCareDuration.NONE)
        # A school age child is age 5 to 13 and enrolled in school; the policy
        # anchors the age at September of the school year, which the model
        # approximates with the annual age.
        age = person("monthly_age", period)
        enrolled_in_school = person("is_in_k12_school", period.this_year)
        school_age = (
            (age >= p.school_age.minimum)
            & (age <= p.school_age.maximum)
            & enrolled_in_school
        )
        part_day = duration == ILCCAPCareDuration.PART_DAY
        non_qualifying_care = in_care & ~(school_age & part_day)
        any_child_in_care = spm_unit.any(in_care)
        all_school_age_part_day = spm_unit.sum(non_qualifying_care) == 0
        return in_school_year & any_child_in_care & all_school_age_part_day
