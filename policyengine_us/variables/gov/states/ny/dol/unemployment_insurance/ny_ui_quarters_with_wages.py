from policyengine_us.model_api import *


class ny_ui_quarters_with_wages(Variable):
    value_type = int
    entity = Person
    label = "New York unemployment insurance quarters with wages"
    definition_period = YEAR
    default_value = 0
    reference = "https://www.nysenate.gov/legislation/laws/LAB/527"
    defined_for = StateCode.NY
