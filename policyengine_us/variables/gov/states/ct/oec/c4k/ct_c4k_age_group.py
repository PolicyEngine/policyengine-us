from policyengine_us.model_api import *


class CTC4KAgeGroup(Enum):
    INFANT_TODDLER = "Infant/Toddler"
    PRE_SCHOOL = "Pre-School"
    SCHOOL_AGE = "School-Age"


class ct_c4k_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = CTC4KAgeGroup
    default_value = CTC4KAgeGroup.SCHOOL_AGE
    definition_period = MONTH
    defined_for = StateCode.CT
    label = "Connecticut Care 4 Kids age group"
    reference = "https://www.ctoec.org/care-4-kids/c4k-providers/c4k-rates/"

    def formula(person, period, parameters):
        age = person("age", period.this_year)
        p = parameters(period).gov.states.ct.oec.c4k.age_threshold.age_group
        return p.calc(age)
