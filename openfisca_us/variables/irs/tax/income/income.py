from openfisca_us.model_api import *


class income_tax_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Income tax refundable credits"
    documentation = "Total refundable income tax credits"
    unit = USD

    def formula(tax_unit, period, parameters):
        credits = parameters(period).irs.credits.refundable
        return add(tax_unit, period, credits)


class iitax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    label = "Federal income tax"
    documentation = "Total federal individual income tax liability."

    def formula(tax_unit, period, parameters):
        return tax_unit(
            "income_tax_before_refundable_credits", period
        ) - tax_unit("income_tax_refundable_credits", period)


income_tax = variable_alias("income_tax", iitax)
