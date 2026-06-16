from policyengine_us.model_api import *


class MSCCPPAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School age"


class ms_ccpp_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = MSCCPPAgeGroup
    default_value = MSCCPPAgeGroup.SCHOOL_AGE
    definition_period = MONTH
    label = "Mississippi CCPP child age group for payment rates"
    defined_for = StateCode.MS
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=14"

    def formula(person, period, parameters):
        age = person("age", period.this_year)
        p = parameters(period).gov.states.ms.dhs.ccpp.age_group
        # The bracket returns 0=INFANT, 1=TODDLER, 2=PRESCHOOL, 3=SCHOOL_AGE,
        # which PolicyEngine maps to the enum index.
        return p.age.calc(age)
