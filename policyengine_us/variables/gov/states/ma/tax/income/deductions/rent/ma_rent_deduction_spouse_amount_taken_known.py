from policyengine_us.model_api import *


class ma_rent_deduction_spouse_amount_taken_known(Variable):
    value_type = bool
    entity = TaxUnit
    label = "External spouse Massachusetts rent deduction amount is confirmed"
    definition_period = YEAR
    default_value = False
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/info-details/deductions-on-rent-paid-in-massachusetts",
        "https://www.mass.gov/doc/2025-form-1-instructions/download",
    )
