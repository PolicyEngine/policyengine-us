from openfisca_us.model_api import *


class md_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD income tax before credits"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("md_taxable_income", period)
