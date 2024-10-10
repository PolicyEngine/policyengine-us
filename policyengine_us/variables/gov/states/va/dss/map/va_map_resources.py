from policyengine_us.model_api import *


class va_map_resources(Variable):
    value_type = float
    entity = Person
    label = "VA MAP resources"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA

    adds = "gov.states.va.dss.map.resources"
