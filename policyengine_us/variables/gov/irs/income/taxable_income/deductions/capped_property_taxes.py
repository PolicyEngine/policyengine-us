from policyengine_us.model_api import *


class capped_property_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Local real estate taxes limited by the federal SALT cap."
    unit = USD
    documentation = "Local real estate taxes limited by the federal SALT cap."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        p = parameters(period).gov.irs.deductions.itemized
        cap = p.salt_and_real_estate.cap[tax_unit("filing_status", period)]
        return min_(property_taxes, cap)
