from policyengine_us.model_api import *


class ak_ccap_charged_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Alaska CCAP provider charged rate per child"
    definition_period = MONTH
    defined_for = StateCode.AK
