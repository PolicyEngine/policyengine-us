from openfisca_us.model_api import *


class ny_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY taxable income"
    unit = USD
    documentation = "NY AGI less taxable income deductions"
    definition_period = YEAR
