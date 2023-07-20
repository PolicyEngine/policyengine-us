from policyengine_us.model_api import *


class total_college_hours(Variable):
    value_type = float
    entity = TaxUnit
    label = "Total annual hours of college attended"
    defined_for = StateCode.SC
    unit = "hour"
    definition_period = YEAR
