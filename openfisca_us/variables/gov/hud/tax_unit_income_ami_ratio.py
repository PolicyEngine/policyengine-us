from openfisca_us.model_api import *


class tax_unit_income_ami_ratio(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ratio of tax unit income to area median income"
    definition_period = YEAR
