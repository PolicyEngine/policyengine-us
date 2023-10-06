from policyengine_us.model_api import *


class tmp(Variable):
    value_type = str
    entity = SPMUnit
    label = "California CalWORKs Child Care Age Eligibility"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.child_care.child_care_time
        days = spm_unit("child_care_days", period)
        weeks = spm_unit("child_care_weeks", period)
        daily_hours = spm_unit("daily_child_care_hours", period)
        weekly_hours = spm_unit("weekly_child_care_hours", period)

        category = where(
            (weekly_hours < p.hourly_care.weekly_child_care_hours) & 
            (daily_hours < p.hourly_care.daily_child_care_hours),
            ["hourly", "part_time"]
        )

        category = where( 
            (daily_hours >= p.daily_care.daily_child_care_hours) &
            (days <= p.daily_care.child_care_days),
            ["daily", "full_time"]
        )

        category = where(
            (daily_hours < p.weekly_care.weekly_child_care_hours),
            ["weekly", "part_time"]
        )

        category = where(
            (daily_hours >= p.weekly_care.weekly_child_care_hours),
            ["weekly", "full_time"]
        )

        category = where(
            (daily_hours < p.monthly_care.weekly_child_care_hours) &
            (weeks == p.monthly_care.child_care_weeks),
            ["monthly", "part_time"]
        )

        category = where(
            (daily_hours >= p.monthly_care.weekly_child_care_hours) &
            (weeks == p.monthly_care.child_care_weeks),
            ["monthly", "full_time"]
        )

        return category
