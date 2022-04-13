from openfisca_us.model_api import *


class income_tax_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Refundable tax credits"
    documentation = "Total refundable income tax credits"
    unit = USD

    def formula(tax_unit, period, parameters):
        credits = parameters(period).irs.credits.refundable
        return add(tax_unit, period, credits)
