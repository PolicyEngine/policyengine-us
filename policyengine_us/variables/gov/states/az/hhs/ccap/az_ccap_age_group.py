from policyengine_us.model_api import *


class AZCCAPAgeGroup(Enum):
    INFANT = "Under age 1"
    TODDLER = "Age 1 or 2"
    PRESCHOOL = "Age 3 through 5"
    SCHOOL_AGE_SUMMER = "Age 6 through 12, May through July"
    SCHOOL_AGE_SCHOOL_YEAR = "Age 6 through 12, August through April"


class az_ccap_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = AZCCAPAgeGroup
    default_value = AZCCAPAgeGroup.PRESCHOOL
    definition_period = MONTH
    label = "Arizona Child Care Assistance Program age group"
    defined_for = StateCode.AZ
    reference = "https://des.az.gov/sites/default/files/dl/CCA-1227A.pdf"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.az.hhs.ccap
        age = person("age", period.this_year)
        month = period.start.month
        is_summer = (month >= p.school_age_summer.start_month) & (
            month <= p.school_age_summer.end_month
        )
        return select(
            [
                age < p.age_group.infant_max,
                age < p.age_group.toddler_max,
                age < p.age_group.preschool_max,
                is_summer,
            ],
            [
                AZCCAPAgeGroup.INFANT,
                AZCCAPAgeGroup.TODDLER,
                AZCCAPAgeGroup.PRESCHOOL,
                AZCCAPAgeGroup.SCHOOL_AGE_SUMMER,
            ],
            default=AZCCAPAgeGroup.SCHOOL_AGE_SCHOOL_YEAR,
        )
