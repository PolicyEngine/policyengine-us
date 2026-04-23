from policyengine_us.model_api import *


class ny_ui_high_quarter_wages(Variable):
    value_type = float
    entity = Person
    label = "NY UI high quarter wages"
    unit = USD
    definition_period = YEAR
    default_value = 0
    reference = "https://www.nysenate.gov/legislation/laws/LAB/527"
