from policyengine_us.model_api import *


class az_families_tax_rebate_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Families Tax Rebate subtraction"
    unit = USD
    documentation = "https://azdor.gov/individuals/arizona-families-tax-rebate"
    reference = "A.R.S. 43-1022 - Subtractions from Arizona Gross Income"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        # The Arizona Families Tax Rebate is subtracted from Arizona gross
        # income because while it is taxable federally, Arizona does not
        # tax it at the state level
        return tax_unit("az_families_tax_rebate_received", period)
