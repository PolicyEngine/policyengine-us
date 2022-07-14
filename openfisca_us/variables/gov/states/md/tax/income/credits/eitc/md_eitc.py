from openfisca_us.model_api import *


class md_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD EITC"
    unit = USD
    documentation = "Maryland EITC"
    definition_period = YEAR

