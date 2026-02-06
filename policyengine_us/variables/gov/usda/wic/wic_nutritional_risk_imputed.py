from policyengine_us.model_api import *


class wic_nutritional_risk_imputed(Variable):
    value_type = bool
    entity = Person
    label = "Imputed WIC nutritional risk"
    definition_period = MONTH
    default_value = True
