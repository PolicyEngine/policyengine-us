from policyengine_us.model_api import *


class taxsim_state_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "State earned income tax credit"
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_eitcs"
