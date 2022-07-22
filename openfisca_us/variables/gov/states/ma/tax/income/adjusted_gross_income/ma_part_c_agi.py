from openfisca_us.model_api import *


class ma_part_c_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part C AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-2"
    defined_for = StateCode.MA

    formula = sum_of_variables(["ma_part_c_gross_income"])
