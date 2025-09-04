from policyengine_us.model_api import *


class ky_homestead_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky homestead exemption"
    unit = USD
    definition_period = YEAR
    defined_for = "ky_homestead_exemption_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ky.tax.income.exemptions.homestead
        exemption_amount = p.amount
        # Add Property Value
        property_value = add(tax_unit, period, ["assessed_property_value"])
        return min_(exemption_amount, property_value)
