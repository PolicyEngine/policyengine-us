from policyengine_us.model_api import *


class state_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "State Child Tax Credit"
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_ctcs"
