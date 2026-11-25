from policyengine_us.model_api import *


class MARentDeductionAllocationDocumentation(Enum):
    VERIFIED = "Required signed allocation statement verified"
    MISSING_OR_INVALID = "Required allocation statement missing or invalid"
    UNKNOWN = "Allocation documentation unknown"


class ma_rent_deduction_allocation_documentation(Variable):
    """Verify applicable consent, identity, year and other-spouse amount facts.

    The model does not create a signature or require an additional statement
    when the supported deduction does not exceed the ordinary separate limit.
    """

    value_type = Enum
    entity = TaxUnit
    possible_values = MARentDeductionAllocationDocumentation
    default_value = MARentDeductionAllocationDocumentation.UNKNOWN
    label = "Massachusetts rent deduction allocation documentation status"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/info-details/deductions-on-rent-paid-in-massachusetts",
        "https://www.mass.gov/doc/2025-form-1-instructions/download",
    )
