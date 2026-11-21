from policyengine_us.model_api import *


class VTRenterCreditDomicileStatus(Enum):
    FULL_YEAR = "Domiciled in Vermont the full year"
    NOT_FULL_YEAR = "Domiciled in Vermont for less than the full year"
    UNREPORTED = "Vermont domicile not reported"


class vt_renter_credit_domicile_status(Variable):
    value_type = Enum
    possible_values = VTRenterCreditDomicileStatus
    default_value = VTRenterCreditDomicileStatus.UNREPORTED
    entity = TaxUnit
    label = "Reported Vermont domicile for the renter credit"
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/154/06066",
        "https://tax.vermont.gov/sites/tax/files/documents/RCC-146-2025.pdf#page=1",
    )
