from policyengine_us.model_api import *


class state_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "State adjusted gross income"
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_agis"
