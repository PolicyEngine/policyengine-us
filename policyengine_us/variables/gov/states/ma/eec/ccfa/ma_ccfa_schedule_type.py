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
    label = "Massachusetts Child Care Financial Assistance (CCFA) schedule type"
    reference = (
        "https://www.mass.gov/doc/eecfy26-rate-increase-chart/download#page=1",
        "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=120",
    )
    # NOTE: EEC bills school age children the before and after school rates on
    # school days and the full day rate only on non-school days. School days
    # are not modeled, so the schedule is an input that defaults to full day.
