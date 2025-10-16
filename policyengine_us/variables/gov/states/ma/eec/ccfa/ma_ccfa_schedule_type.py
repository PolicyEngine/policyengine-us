from policyengine_us.model_api import *


class MassachusettsCCFAScheduleType(Enum):
    FULL_DAY = "Full Day"
    BEFORE_ONLY = "Before Only"
    AFTER_ONLY = "After Only"
    BEFORE_AND_AFTER = "Before and After"


class ma_ccfa_schedule_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = MassachusettsCCFAScheduleType
    default_value = MassachusettsCCFAScheduleType.FULL_DAY
    definition_period = MONTH
    defined_for = StateCode.MA
    label = (
        "Massachusetts Child Care Financial Assistance (CCFA) schedule type"
    )
    reference = "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download"
