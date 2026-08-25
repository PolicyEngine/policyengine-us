from policyengine_us.model_api import *


class ny_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York child care subsidies"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = "https://www.nysenate.gov/legislation/laws/SOS/410-U"
    adds = ["ny_ccap"]
