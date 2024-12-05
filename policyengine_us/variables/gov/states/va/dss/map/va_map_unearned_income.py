from policyengine_us.model_api import *


class va_map_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "VA MAP unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA

    adds = "gov.states.va.dss.map.unearned"
