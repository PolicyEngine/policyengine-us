from policyengine_us.model_api import *


class il_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois Property Tax Credit"
    unit = USD
    definition_period = YEAR

    defined_for = "il_is_exemption_eligible"

    def formula(tax_unit, period, parameters):
        ptax_paid = add(tax_unit, period, ["real_estate_taxes"])
        pre_credit_tax = tax_unit(
            "il_income_tax_before_non_refundable_credits", period
        )
        p = parameters(period).gov.states.il.tax.income.credits
        return min_(ptax_paid * p.property_tax.rate, pre_credit_tax)
