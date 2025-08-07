from policyengine_us.model_api import *


class state_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "State Property Tax Credit"
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_property_tax_credits"
