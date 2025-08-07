from policyengine_us.model_api import *


class state_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "State taxable income"
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_taxable_incomes"
