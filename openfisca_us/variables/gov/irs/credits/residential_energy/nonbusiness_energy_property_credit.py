from openfisca_us.model_api import *


class residential_energy_efficient_property_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Residential energy efficient property tax credit"
    unit = USD
