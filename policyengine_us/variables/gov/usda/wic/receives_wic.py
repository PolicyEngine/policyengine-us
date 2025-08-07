from policyengine_us.model_api import *


class receives_wic(Variable):
    value_type = bool
    entity = Person
    label = "Reported to receive WIC"
    definition_period = MONTH
