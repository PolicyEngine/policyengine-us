from policyengine_us.model_api import *


class GACAPSCareType(Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    BEFORE_AFTER_SCHOOL = "Before and After School"


class ga_caps_care_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = GACAPSCareType
    default_value = GACAPSCareType.FULL_TIME
    definition_period = MONTH
    label = "Georgia CAPS care type"
    defined_for = StateCode.GA
    reference = "https://caps.decal.ga.gov/assets/downloads/CAPS/AppendixC-CAPS%20Reimbursement%20Rates.pdf#page=1"
