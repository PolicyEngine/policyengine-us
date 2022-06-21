from openfisca_us.model_api import *


class ut_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah Taxable Income"
    unit = USD
    definition_period = YEAR
