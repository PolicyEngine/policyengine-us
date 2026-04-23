from policyengine_us.model_api import *


class ny_ui_weeks_unemployed(Variable):
    value_type = int
    entity = Person
    label = "NY UI weeks unemployed"
    unit = "week"
    definition_period = YEAR
    default_value = 0
    reference = "https://www.nysenate.gov/legislation/laws/LAB/590"
