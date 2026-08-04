from policyengine_us.model_api import *


class MOCCSAgeGroup(Enum):
    INFANT_TODDLER = "Infant/Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School age"


class mo_ccs_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = MOCCSAgeGroup
    default_value = MOCCSAgeGroup.SCHOOL_AGE
    definition_period = MONTH
    label = "Missouri Child Care Subsidy child age group for payment rates"
    defined_for = StateCode.MO
    reference = "https://dese.mo.gov/childhood/child-care-subsidy/payments"

    def formula(person, period, parameters):
        age = person("age", period.this_year)
        p = parameters(period).gov.states.mo.dese.ccs.age_group
        # The age bracket returns the MOCCSAgeGroup enum index:
        # 0 = INFANT_TODDLER, 1 = PRESCHOOL, 2 = SCHOOL_AGE.
        return p.age.calc(age)
