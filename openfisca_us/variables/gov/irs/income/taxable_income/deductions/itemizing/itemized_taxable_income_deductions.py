from openfisca_us.model_api import *


class itemized_taxable_income_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Itemized taxable income deductions"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables("irs.deductions.itemized_deductions")
