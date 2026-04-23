from policyengine_us.model_api import *


class WAPFMLLeaveType(Enum):
    FAMILY = "Family"
    MEDICAL = "Medical"
    COMBINED = "Combined"
    MEDICAL_WITH_PREGNANCY_INCAPACITY = "Medical with pregnancy incapacity"
    COMBINED_WITH_PREGNANCY_INCAPACITY = "Combined with pregnancy incapacity"
    NONE = "None"


class wa_pfml_leave_type(Variable):
    value_type = Enum
    entity = Person
    label = "Washington PFML leave type"
    definition_period = YEAR
    possible_values = WAPFMLLeaveType
    default_value = WAPFMLLeaveType.NONE
    defined_for = StateCode.WA
    reference = "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.020"
