from policyengine_us.model_api import *


class RICCAPCenterAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School Age"


class ri_ccap_center_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = RICCAPCenterAgeGroup
    default_value = RICCAPCenterAgeGroup.PRESCHOOL
    definition_period = MONTH
    label = "Rhode Island CCAP licensed center age group"
    defined_for = StateCode.RI
    reference = "https://dhs.ri.gov/media/9356/download?language=en"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ri.dhs.ccap.age_group.center
        age = person("age", period.this_year)
        is_in_school = person("is_in_k12_school", period.this_year)
        return select(
            [
                age < p.infant_max,
                age < p.toddler_max,
                ~is_in_school,
            ],
            [
                RICCAPCenterAgeGroup.INFANT,
                RICCAPCenterAgeGroup.TODDLER,
                RICCAPCenterAgeGroup.PRESCHOOL,
            ],
            default=RICCAPCenterAgeGroup.SCHOOL_AGE,
        )
