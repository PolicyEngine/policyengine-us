from openfisca_us.model_api import *


class sewage_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Sewage expense"
    unit = USD
    definition_period = YEAR
