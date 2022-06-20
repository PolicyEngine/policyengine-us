from openfisca_us.model_api import *


class utility_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Utility expenses"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(
        [
            "heating_cooling_expense",
            "gas_expense",
            "electricity_expense",
            "trash_expense",
            "water_expense",
            "sewage_expense",
            "phone_expense",
        ]
    )
