from policyengine_us.model_api import *


class flat_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Flat tax"
    unit = USD
    documentation = "Flat income tax on federal AGI or gross income."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.contrib.ubi_center.flat_tax.rate
        # Gross income flat tax.
        gross_income = add(tax_unit, period, ["positive_gross_income"])
        gross_income_flat_tax = gross_income * p.gross_income
        # AGI flat tax.
        agi = tax_unit("positive_agi", period)
        agi_flat_tax = agi * p.agi
        return gross_income_flat_tax + agi_flat_tax
