from openfisca_us.model_api import *


class in_rent(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN rent"
    unit = USD
    definition_period = YEAR
    documentation = "Rent paid on a principal place of residence that was subject to Indiana property tax."
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-6"