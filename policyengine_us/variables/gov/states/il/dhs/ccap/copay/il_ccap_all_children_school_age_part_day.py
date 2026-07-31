from policyengine_us.model_api import *


class il_ccap_all_children_school_age_part_day(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Illinois CCAP all children in care school-age part-day"
    defined_for = StateCode.IL
    reference = "https://www.dhs.state.il.us/page.aspx?item=54862"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap
        person = spm_unit.members
        eligible_child = person("il_ccap_eligible_child", period)
        hours = person("childcare_hours_per_day", period.this_year)
        in_care = eligible_child & (hours > 0)
        age = person("monthly_age", period)
        school_age = (
            (age >= p.copay.school_age_minimum)
            & (age <= p.copay.school_age_maximum)
            & person("is_full_time_student", period.this_year)
        )
        part_day = hours < p.rates.duration.part_day_hours_limit
        qualifying_child = in_care & school_age & part_day
        return (spm_unit.sum(in_care) > 0) & (
            spm_unit.sum(qualifying_child) == spm_unit.sum(in_care)
        )
