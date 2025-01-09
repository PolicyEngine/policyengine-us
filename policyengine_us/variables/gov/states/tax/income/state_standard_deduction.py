from policyengine_us.model_api import *


class state_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "State standard deduction"
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_standard_deductions"
