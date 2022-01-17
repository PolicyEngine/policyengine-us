from openfisca_us.model_api import *


class childcare_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "Child care expenses"
    documentation = "Out of pocket spending on childcare"
    definition_period = YEAR
    unit = USD
