from policyengine_us.model_api import *


class va_famis_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA FAMIS Plus earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA

    adds = "gov.states.va.dss.map.earned"
