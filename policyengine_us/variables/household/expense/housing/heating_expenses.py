from policyengine_us.model_api import *


class heating_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit heating cost"
    unit = USD
    definition_period = YEAR

    adds = ["heating_expense_person"]
