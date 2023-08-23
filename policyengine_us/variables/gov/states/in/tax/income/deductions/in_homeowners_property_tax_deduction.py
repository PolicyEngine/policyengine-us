from policyengine_us.model_api import *


class in_homeowners_property_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana homeowner's residential property tax deduction"
    unit = USD
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income
        filing_status = tax_unit("filing_status", period)
        max_deduction = p.deductions.homeowners_property_tax.max[filing_status]
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        return min_(property_tax, max_deduction)
