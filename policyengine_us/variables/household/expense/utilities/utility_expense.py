from policyengine_us.model_api import *


class utility_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Utility expenses"
    unit = USD
    definition_period = YEAR

    adds = [
        "heating_cooling_expense",
        "gas_expense",
        "electricity_expense",
        "trash_expense",
        "water_expense",
        "sewage_expense",
        "phone_expense",
    ]
