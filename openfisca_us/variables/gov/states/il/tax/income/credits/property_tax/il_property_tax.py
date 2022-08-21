from openfisca_us.model_api import *

class il_property_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL Property Tax For The Real Estate That Includes The Principal Residence"
    unit = USD
    definition_period = YEAR
    reference = ""