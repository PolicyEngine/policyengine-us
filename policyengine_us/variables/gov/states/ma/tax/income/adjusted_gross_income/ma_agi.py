from policyengine_us.model_api import *


class ma_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-2"
    defined_for = StateCode.MA

    formula = sum_of_variables(
        [
            "ma_part_a_gross_income",
            "ma_part_b_gross_income",
            "ma_part_c_gross_income",
        ]
    )
