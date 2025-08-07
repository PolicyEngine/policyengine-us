from policyengine_us.model_api import *


class state_withheld_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "state income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_withheld_income_tax"
