from policyengine_us.model_api import *


class homeowners_association_fees(Variable):
    value_type = float
    entity = SPMUnit
    label = "Homeowners association fees"
    unit = USD
    definition_period = YEAR
