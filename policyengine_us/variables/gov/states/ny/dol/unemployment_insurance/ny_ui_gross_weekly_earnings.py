from policyengine_us.model_api import *


class ny_ui_gross_weekly_earnings(Variable):
    value_type = float
    entity = Person
    label = "NY UI gross weekly earnings"
    unit = USD
    definition_period = YEAR
    default_value = 0
    reference = "https://www.nysenate.gov/legislation/laws/LAB/590"
