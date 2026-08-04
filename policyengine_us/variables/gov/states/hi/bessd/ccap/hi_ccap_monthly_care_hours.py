from policyengine_us.model_api import *


class hi_ccap_monthly_care_hours(Variable):
    value_type = float
    entity = Person
    unit = "hour"
    label = "Hawaii CCAP effective monthly hours of care"
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/bessd/files/2013/01/HAR-17-798.2-Child-Care-Services-Rules.pdf#page=29"

    def formula(person, period, parameters):
        # HAR 17-798.2-14(b)(1): the allowance uses the lesser of the child's
        # monthly care hours and the caretaker's authorized monthly activity
        # hours. childcare_hours_per_week is YEAR-defined; read with
        # period.this_year and convert weekly hours to a monthly count.
        weekly_care_hours = person("childcare_hours_per_week", period.this_year)
        monthly_care_hours = weekly_care_hours * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
        activity_hours = person.spm_unit("hi_ccap_authorized_activity_hours", period)
        return min_(monthly_care_hours, activity_hours)
