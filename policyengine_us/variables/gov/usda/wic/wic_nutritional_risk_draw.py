from policyengine_us.model_api import *


class wic_nutritional_risk_draw(Variable):
    value_type = float
    entity = Person
    label = "Random draw for WIC nutritional risk assessment"
    definition_period = MONTH
    default_value = 0
