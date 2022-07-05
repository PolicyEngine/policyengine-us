from openfisca_us.model_api import *


class mo_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO property tax credit"
    unit = USD
    definition_period = YEAR
    reference = ()
