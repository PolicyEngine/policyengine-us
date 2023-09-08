from policyengine_us.model_api import *


class mi_homestead_refundable(Variable):
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

        non_refundable_amount = tax_unit("mi_homestead_non_refundable", period)

        property_value = add(tax_unit, period, ["assessed_property_value"])
        rents = add(tax_unit, period, ["rent"])
        total = property_value + rents * p.rate.rent

        # Worksheet line 35
        return max_(total - non_refundable_amount, 0)
