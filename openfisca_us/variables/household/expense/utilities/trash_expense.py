from openfisca_us.model_api import *


class trash_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Trash expense"
    unit = USD
    definition_period = YEAR
