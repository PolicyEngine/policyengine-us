from openfisca_us.model_api import *


class gas_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Gas expense"
    unit = USD
    definition_period = YEAR
