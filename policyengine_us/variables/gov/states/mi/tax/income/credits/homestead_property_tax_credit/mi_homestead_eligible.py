from policyengine_us.model_api import *


class mi_homestead_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Michigan Homestead Property Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.homestead_property_tax_credit

        property_value_eligible = (
            add(tax_unit, period, ["assessed_property_value"])
            <= p.max.property_value
        )

        refundable_amount_eligible = (
            tax_unit("mi_homestead_refundable", period) > 0
        )

        return refundable_amount_eligible & property_value_eligible
