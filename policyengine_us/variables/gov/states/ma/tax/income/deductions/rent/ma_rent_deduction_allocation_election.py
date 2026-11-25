from policyengine_us.model_api import *


class MARentDeductionAllocationElection(Enum):
    NO_ALTERNATIVE = "No alternative allocation elected"
    ALTERNATIVE = "Alternative allocation elected"
    UNKNOWN = "Allocation election unknown"


class ma_rent_deduction_allocation_election(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = MARentDeductionAllocationElection
    default_value = MARentDeductionAllocationElection.UNKNOWN
    label = "Massachusetts rent deduction separate-return allocation election"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/info-details/deductions-on-rent-paid-in-massachusetts",
        "https://www.mass.gov/doc/2025-form-1-instructions/download",
    )
