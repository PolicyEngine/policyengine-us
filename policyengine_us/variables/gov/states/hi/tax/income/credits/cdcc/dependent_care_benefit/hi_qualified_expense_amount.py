from policyengine_us.model_api import *


class hi_qualified_expense_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii amount of qualified expenses incurred for the care of qualifying persons"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
