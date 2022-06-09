from openfisca_us.model_api import *


class e07260(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Residential energy credit from Form 5695"
    unit = USD


residential_energy_credit = variable_alias("residential_energy_credit", e07260)
