from policyengine_us.model_api import *

class nc_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ncdor.gov/taxes-forms/individual-income-tax/north-carolina-standard-deduction-or-north-carolina-itemized-deductions "
    )
    defined_for = StateCode.nc

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nc.tax.income
        filing_status = tax_unit("filing_status", period)
        
        mortgage_deduction = min(p.deductions.itemized.mortgage_limit,
        add(tax_unit, period, ["mortgage_taxes"]))
        
        property_taxes = min(p.deductions.itemized.property_taxes_limit[filing_status],
        add(tax_unit, period, ["property_taxes"]))

        itemized_deductions = mortgage_deduction + property_taxes
        
        return itemized_deductions
