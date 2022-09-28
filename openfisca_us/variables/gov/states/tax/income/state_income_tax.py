from openfisca_us.model_api import *


class state_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax"
    unit = USD
    definition_period = YEAR

    formula_2021 = sum_of_variables(
<<<<<<< HEAD
        ["ma_income_tax", "wa_income_tax", "md_income_tax", "ny_income_tax"]
=======
        [
            "ma_income_tax",
            "wa_income_tax",
            "md_income_tax",
            "ny_income_tax",
            "pa_income_tax",
        ]
>>>>>>> 32731216fc851e6adc043ee79ded21fad318b131
    )
