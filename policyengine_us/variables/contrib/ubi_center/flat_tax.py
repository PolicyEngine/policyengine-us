from policyengine_us.model_api import *


class flat_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Flat tax"
    unit = USD
    documentation = "Flat income tax on federal AGI or gross income."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.contrib.ubi_center.flat_tax
        # Gross income flat tax.
        gross_income = add(tax_unit, period, ["positive_gross_income"])
        gross_income_flat_tax = gross_income * p.rate.gross_income
        # AGI flat tax.
        filing_status = tax_unit("filing_status", period)
        exemption = p.exemption.agi[filing_status]
        agi = tax_unit("positive_agi", period)
        excess_agi = max_(agi - exemption, 0)
        agi_flat_tax = excess_agi * p.rate.agi
        return gross_income_flat_tax + agi_flat_tax
