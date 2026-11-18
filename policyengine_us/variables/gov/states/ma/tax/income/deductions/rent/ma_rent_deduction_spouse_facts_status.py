from policyengine_us.model_api import *


class MARentDeductionSpouseFactsStatus(Enum):
    VERIFIED_EXTERNAL_RETURN = "External spouse return and identity verified"
    VERIFIED_PAIR = "Paired returns verified but allocation unsupported"
    CONTRADICTORY = "Spouse return facts contradictory"
    UNKNOWN = "Spouse return facts unknown"


class ma_rent_deduction_spouse_facts_status(Variable):
    """Document the external spouse without inferring a link from entity groups."""

    value_type = Enum
    entity = TaxUnit
    possible_values = MARentDeductionSpouseFactsStatus
    default_value = MARentDeductionSpouseFactsStatus.UNKNOWN
    label = "Massachusetts rent deduction spouse return facts status"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/info-details/deductions-on-rent-paid-in-massachusetts",
        "https://www.mass.gov/doc/2025-form-1-instructions/download",
    )
