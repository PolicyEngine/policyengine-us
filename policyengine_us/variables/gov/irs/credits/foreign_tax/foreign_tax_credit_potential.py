from policyengine_us.model_api import *


class foreign_tax_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Potential value of the Foreign tax credit"
    definition_period = YEAR
    documentation = "Foreign tax credit from Form 1116"
    unit = USD
