from policyengine_us.model_api import *


class mi_homestead_property_tax_credit_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan Homestead Property Tax Credit eligibility"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.homestead_property_tax_credit

        property_value = add(tax_unit, period, ["assessed_property_value"])
        rents = add(tax_unit, period, ["rent"])
        refundable_amount = tax_unit(
            "mi_homestead_property_tax_credit_refundable", period
        )

        return where(
            rents > 0,
            refundable_amount > 0,
            (refundable_amount > 0) & (property_value < p.max_property_value),
        )
