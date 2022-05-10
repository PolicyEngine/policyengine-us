from openfisca_us.model_api import *


class c21060(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Gross itemized deductions"
    unit = USD
    documentation = (
        "Itemized deductions before phase-out (zero for non-itemizers)"
    )

    formula = sum_of_variables("irs.deductions.deductions_if_itemizing")
