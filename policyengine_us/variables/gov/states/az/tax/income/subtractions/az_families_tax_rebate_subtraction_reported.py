from policyengine_us.model_api import *


class az_families_tax_rebate_subtraction_reported(Variable):
    value_type = float
    entity = TaxUnit
    label = "Reported Arizona Families Tax Rebate subtraction"
    unit = USD
    documentation = (
        "Amount of Arizona Families Tax Rebate received in the tax year and "
        "included in federal AGI."
    )
    reference = "A.R.S. 43-1022 - Subtractions from Arizona Gross Income"
    definition_period = YEAR
    default_value = 0

    def formula(tax_unit, period, parameters):
        # Returning an explicit zero prevents the system-wide input carry-over
        # fallback from reusing a prior year's reported amount.
        return 0
