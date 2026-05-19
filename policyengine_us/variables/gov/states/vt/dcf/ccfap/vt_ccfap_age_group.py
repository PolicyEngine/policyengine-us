from policyengine_us.model_api import *


class VTCCFAPAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School Age"


class vt_ccfap_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = VTCCFAPAgeGroup
    default_value = VTCCFAPAgeGroup.INFANT
    definition_period = MONTH
    defined_for = StateCode.VT
    label = "Vermont CCFAP age group"
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Regulations.pdf#page=3"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.vt.dcf.ccfap.age_group
        age = person("age", period.this_year)
        age_months = age * MONTHS_IN_YEAR
        return p.months.calc(age_months)
