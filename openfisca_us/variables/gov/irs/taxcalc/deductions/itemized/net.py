from openfisca_us.model_api import *


class c21040(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Phased-out itemized deductions"
    unit = USD
    documentation = "Itemized deductions that are phased out"
