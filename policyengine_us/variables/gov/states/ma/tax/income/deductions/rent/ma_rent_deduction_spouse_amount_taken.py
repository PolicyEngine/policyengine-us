from policyengine_us.model_api import *


class ma_rent_deduction_spouse_amount_taken(Variable):
    """Actual external spouse deduction on the corresponding documented return.

    This is an observed external-return fact, not an entered own deduction or
    the result of a simultaneous-spouse allocation solver.
    """

    value_type = float
    entity = TaxUnit
    label = "Massachusetts rent deduction actually taken by the external spouse"
    unit = USD
    definition_period = YEAR
    default_value = -1
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/info-details/deductions-on-rent-paid-in-massachusetts",
        "https://www.mass.gov/doc/2025-form-1-instructions/download",
    )
