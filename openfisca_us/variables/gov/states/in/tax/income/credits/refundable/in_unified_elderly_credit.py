from openfisca_us.model_api import *


class in_unified_elderly_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN unfied elderly credit"
    definition_period = YEAR
    documentation = "Unified tax credit for the elderly."
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-3-9"
    # formula to be added later
