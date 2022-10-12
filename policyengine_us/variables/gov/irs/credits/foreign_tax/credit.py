from policyengine_us.model_api import *


class foreign_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Foreign tax credit from Form 1116"
    unit = USD
