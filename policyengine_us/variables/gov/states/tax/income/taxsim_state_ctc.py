from policyengine_us.model_api import *


class taxsim_state_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "State child tax credit"
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_ctcs"
