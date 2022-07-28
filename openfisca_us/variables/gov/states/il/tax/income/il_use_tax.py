from openfisca_us.model_api import *

class il_use_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL use tax"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        agi = tax_unit("agi", period)
        p = parameters(period).openfisca_us.gov.states.il.tax.income.use_tax
        return where(agi > 100000, p.rate * agi, p.amount.calc(agi))