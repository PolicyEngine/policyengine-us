from policyengine_us.model_api import *


class marital_unit_id(Variable):
    value_type = int
    entity = MaritalUnit
    label = "Marital unit ID"
    definition_period = YEAR
