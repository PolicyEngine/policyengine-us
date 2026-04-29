from policyengine_us.model_api import *


class il_property_tax_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois Property Tax Credit"
    unit = USD
    definition_period = YEAR

    defined_for = "il_is_exemption_eligible"

    def formula(tax_unit, period, parameters):
        ptax_paid = add(tax_unit, period, ["real_estate_taxes"])
        p = parameters(period).gov.states.il.tax.income.credits
        return ptax_paid * p.property_tax.rate
