from policyengine_us.model_api import *


class MECCAPAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School Age"


class me_ccap_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = MECCAPAgeGroup
    default_value = MECCAPAgeGroup.SCHOOL_AGE
    definition_period = MONTH
    defined_for = StateCode.ME
    label = "Maine CCAP child age group"
    reference = "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/CCAP%20Full%20Rule%208.18.2025_1.pdf#page=7"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.me.dhhs.ccap.age_groups
        age = person("monthly_age", period)
        age_months = age * MONTHS_IN_YEAR
        return select(
            [
                age_months < p.infant_max_months,
                age_months < p.toddler_max_months,
                age < p.preschool_max_years,
            ],
            [
                MECCAPAgeGroup.INFANT,
                MECCAPAgeGroup.TODDLER,
                MECCAPAgeGroup.PRESCHOOL,
            ],
            default=MECCAPAgeGroup.SCHOOL_AGE,
        )
