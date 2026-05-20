from policyengine_us.model_api import *


class taxsim_state_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "State child and dependent care tax credit"
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_cdccs"
