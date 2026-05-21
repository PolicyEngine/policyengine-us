from policyengine_us.model_api import *


class pa_property_tax_or_rent_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Pennsylvania Property Tax/Rent Rebate"
    unit = USD
    definition_period = YEAR
    reference = "https://www.pa.gov/agencies/revenue/ptrr"
    defined_for = "pa_property_tax_or_rent_rebate_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.pa.tax.property.property_tax_or_rent_rebate
        income = tax_unit("pa_property_tax_or_rent_rebate_income", period)
        rent_rebate_base = p.rent_rate * add(tax_unit, period, ["rent"])
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        return min_(p.amount.calc(income), property_tax + rent_rebate_base)
