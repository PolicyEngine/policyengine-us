from openfisca_us.model_api import *


class tax_unit_id(Variable):
    value_type = float
    entity = TaxUnit
    label = "Unique reference for this tax unit"
    definition_period = ETERNITY
