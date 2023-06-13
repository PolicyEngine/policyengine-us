from policyengine_us.model_api import *


class mi_homestead_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan Homestead Property Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.homestead_property_tax_credit
        total_household_resources = tax_unit("mi_household_resources", period)
        rent = tax_unit("rents", period)
        property_value = tax_unit, sum("assessed_property_value", period)
        eligibility = rent > 0 & property_value < p.max_property_value
        percentage = p.percentage.calc(total_household_resources)
        return eligibility * (p.max_amount * percentage)
