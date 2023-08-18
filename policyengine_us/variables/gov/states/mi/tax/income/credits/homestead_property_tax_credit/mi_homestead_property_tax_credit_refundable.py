from policyengine_us.model_api import *


class mi_homestead_property_tax_credit_refundable(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan refundable Homestead Property Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.homestead_property_tax_credit

        non_refundable_amount = tax_unit(
            "mi_homestead_property_tax_credit_non_refundable", period
        )

        property_value = add(tax_unit, period, ["assessed_property_value"])
        rents = add(tax_unit, period, ["rent"])

        rent_refundable_amount = max_(
            rents * p.rent_rate - non_refundable_amount, 0
        )
        property_refundable_amount = max_(
            property_value - non_refundable_amount, 0
        )

        return where(
            rents > 0,
            rent_refundable_amount,
            property_refundable_amount,
        )
