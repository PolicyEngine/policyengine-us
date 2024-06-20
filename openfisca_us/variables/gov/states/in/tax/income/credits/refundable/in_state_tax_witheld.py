from openfisca_us.model_api import *


class in_state_tax_witheld(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN credit for Indiana state taxes withheld"
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-3-1"
