from policyengine_us.model_api import *


class state_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "State itemized deductions"
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_itemized_deductions"
