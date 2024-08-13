from policyengine_us.model_api import *


class flat_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Flat tax"
    unit = USD
    documentation = "Flat income tax on federal AGI or gross income."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        income = tax_unit("positive_agi", period)
        p = parameters(period).gov.contrib.ubi_center.flat_tax
        if p.flat_tax_on_gross_income:
            income = add(tax_unit, period, ["irs_gross_income"])
        return p.rate * income
