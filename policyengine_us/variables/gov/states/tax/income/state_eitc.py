from policyengine_us.model_api import *


class state_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "State Earned Income Tax Credit"
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_eitcs"
