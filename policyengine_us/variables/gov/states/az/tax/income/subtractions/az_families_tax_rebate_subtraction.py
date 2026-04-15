from policyengine_us.model_api import *


class az_families_tax_rebate_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Families Tax Rebate subtraction"
    unit = USD
    documentation = (
        "Amount of Arizona Families Tax Rebate received in the tax year and "
        "included in federal AGI."
    )
    reference = "A.R.S. 43-1022 - Subtractions from Arizona Gross Income"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        # Use only same-year reported amounts. Keeping this as a computed
        # variable avoids auto-carrying a prior year's reported subtraction.
        return tax_unit("az_families_tax_rebate_subtraction_reported", period)
