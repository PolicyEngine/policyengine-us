from policyengine_us.model_api import *


class ny_ui_weekly_hours_worked(Variable):
    value_type = float
    entity = Person
    label = "NY UI weekly hours worked"
    unit = "hour"
    definition_period = YEAR
    default_value = 0
    reference = "https://www.nysenate.gov/legislation/laws/LAB/590"
