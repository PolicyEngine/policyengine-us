from openfisca_us.model_api import *


class above_the_line_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Above-the-line deductions"
    unit = USD
    documentation = "Deductions applied to reach adjusted gross income from gross income."
    definition_period = YEAR

    formula = sum_of_variables("irs.ald.deductions")