from openfisca_us.model_api import *


class in_nol(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN nol"
    unit = USD
    definition_period = YEAR
    documentation = "Net operating losses allowable for deduction in Indiana."
    reference = (
        "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-2.5"
    )
