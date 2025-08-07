from policyengine_us.model_api import *


class er_visit_expense(Variable):
    value_type = float
    entity = Person
    label = "Emergency room visit expenses"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.hhs.cms.moop_per_capita"
