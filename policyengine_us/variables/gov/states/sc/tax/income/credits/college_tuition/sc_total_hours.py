from policyengine_us.model_api import *


class sc_total_hours(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina college total hours"
    defined_for = StateCode.SC
    unit = "hour"
    definition_period = YEAR
