from policyengine_us.model_api import *


class ma_rent_deduction_qualifying_rent_paid_known(Variable):
    """Confirm payer identity, actual return role/year and qualifying rent base.

    The receipt must resolve the residence and payment-period qualifications and
    all rent exclusions, including a known zero. An inferred role or generic
    housing expense cannot establish these facts without the matching receipt.
    """

    value_type = bool
    entity = Person
    label = "Qualifying Massachusetts rent paid and payer facts are confirmed"
    definition_period = YEAR
    default_value = False
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/info-details/deductions-on-rent-paid-in-massachusetts",
        "https://www.mass.gov/doc/2025-form-1-nrpy-instructions/download",
    )
