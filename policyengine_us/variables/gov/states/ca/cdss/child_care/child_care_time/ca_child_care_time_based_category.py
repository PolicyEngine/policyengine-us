from policyengine_us.model_api import *

class ca_child_care_time_based_category(Variable):
    value_type = str
    entity = SPMUnit
    label = "California CalWORKs Child Care Age Eligibility"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.child_care.child_care_time
        days = spm_unit("ca_child_care_days", period)
        weeks = spm_unit("ca_child_care_weeks", period)
        daily_hours = spm_unit("ca_child_care_daily_hours", period)
        weekly_hours = spm_unit("ca_child_care_weekly_hours", period)

        if (weekly_hours < p.hourly_care.weekly_child_care_hours) & (daily_hours < p.hourly_care.daily_child_care_hours):
            category = ["hourly", "part_time"]
        
        if (daily_hours >= p.daily_care.daily_child_care_hours) & (days <= p.daily_care.child_care_days):
             category = ["daily", "full_time"]

        if (daily_hours < p.weekly_care.weekly_child_care_hours):
            category = ["weekly", "part_time"]

        if (daily_hours >= p.weekly_care.weekly_child_care_hours):
            category = ["weekly", "full_time"]

        if (daily_hours < p.monthly_care.weekly_child_care_hours) & (weeks == p.monthly_care.child_care_weeks):
            category = ["monthly", "part_time"]
        
        if (daily_hours >= p.monthly_care.weekly_child_care_hours) & (weeks == p.monthly_care.child_care_weeks):
            category = ["monthly", "full_time"]

        return category