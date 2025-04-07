from policyengine_us.model_api import *


class household_weight(Variable):
    value_type = float
    entity = Household
    label = "Household weight"
    definition_period = YEAR
    uprating = "calibration.gov.census.populations.total"
