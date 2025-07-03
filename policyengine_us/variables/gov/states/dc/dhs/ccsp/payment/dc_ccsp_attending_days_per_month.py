from policyengine_us.model_api import *


class dc_ccsp_attending_days_per_month(Variable):
    value_type = int
    entity = Person
    label = "DC Child Care Subsidy Program (CCSP) attending days per month"
    definition_period = MONTH
    defined_for = StateCode.DC
