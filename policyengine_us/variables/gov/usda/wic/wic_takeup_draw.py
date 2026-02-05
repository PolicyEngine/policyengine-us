from policyengine_us.model_api import *


class wic_takeup_draw(Variable):
    value_type = float
    entity = Person
    label = "Random draw for WIC takeup decision"
    definition_period = MONTH
    default_value = 0
