from openfisca_us.model_api import *


class electricity_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Electricity expense"
    unit = "currency-USD"
    definition_period = YEAR
