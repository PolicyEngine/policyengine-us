from policyengine_us.model_api import *


class vt_renter_credit_months_rented(Variable):
    value_type = int
    entity = TaxUnit
    label = "Reported months renting in Vermont for the renter credit"
    unit = "month"
    definition_period = YEAR
    defined_for = StateCode.VT
    # Count distinct qualifying calendar months for the RCC-146 claimant.
    default_value = -1
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/154/06062",
        "https://tax.vermont.gov/sites/tax/files/documents/RCC-146-2025.pdf#page=1",
    )
