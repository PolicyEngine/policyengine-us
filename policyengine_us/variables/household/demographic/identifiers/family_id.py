from policyengine_us.model_api import *


class family_id(Variable):
    value_type = float
    entity = Family
    label = "Unique reference for this family"
    definition_period = YEAR
