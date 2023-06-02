from policyengine_us.model_api import *

# policyengine-core test ./policyengine_us/tests/policy/baseline/gov/states/mi/

class mi_homestead_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan Homestead Property Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.state.mi.homestead_property_tax_credit
        household_resources = p.household_resources
        total_household_resources = add(tax_unit, period, ["household_resources"])
        percentage = p.phase_out.threshold[total_household_resources]
        return p.max_amount * percentage

    #def formula(tax_unit, period, parameters):
        #property_tax = household("property_tax", period)
    #    p = parameters(period).gov.state.mi.homestead_property_tax_credit
    #    household_resources = p.household_resources
    #    total_household_resources = add(tax_unit, period, ["household_resources"])
    #    credit_percentage = total_household_resources * p.phase_out
    #    return min(p.max_amount * credit_percentage, p.max_amount)