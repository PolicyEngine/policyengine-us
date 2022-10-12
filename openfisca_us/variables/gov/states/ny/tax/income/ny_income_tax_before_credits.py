from policyengine_us.model_api import *


class ny_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY income tax before credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY

    formula = sum_of_variables(
        [
            "ny_main_income_tax",
            "ny_supplemental_tax",
        ]
    )
