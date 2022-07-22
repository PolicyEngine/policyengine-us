from openfisca_us.model_api import *


class ma_part_c_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part C gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-2"  # (b)(3)

    def formula(tax_unit, period, parameters):
        return max_(0, add(tax_unit, period, ["long_term_capital_gains"]))
