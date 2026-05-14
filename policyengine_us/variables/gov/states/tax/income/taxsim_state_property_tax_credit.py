from policyengine_us.model_api import *


class taxsim_state_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "State property tax credit"
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_property_tax_credits"
