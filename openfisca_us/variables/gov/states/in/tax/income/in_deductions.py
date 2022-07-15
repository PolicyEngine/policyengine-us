from openfisca_us.model_api import *


class in_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN deductions"
    unit = USD
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3"
