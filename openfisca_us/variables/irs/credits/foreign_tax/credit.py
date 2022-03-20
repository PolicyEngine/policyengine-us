from openfisca_us.model_api import *


class e07300(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Foreign tax credit from Form 1116"
    unit = USD


foreign_tax_credit = variable_alias("foreign_tax_credit", e07300)
