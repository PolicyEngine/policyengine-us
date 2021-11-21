from openfisca_core.model_api import *
from openfisca_us.entities import *


class person_id(Variable):
    value_type = int
    entity = Person
    label = u"Unique reference for this person"
    definition_period = ETERNITY


class people(Variable):
    value_type = float
    entity = Person
    label = u"People represented"
    definition_period = YEAR
    default_value = 1.0


class person_weight(Variable):
    value_type = float
    entity = Person
    label = u"Person weight"
    definition_period = YEAR


class age(Variable):
    value_type = float
    entity = Person
    label = u"Age"
    definition_period = YEAR


class AgeGroup(Enum):
    CHILD = "Child"
    WORKING_AGE = "Working-age"
    SENIOR = "Senior"


class age_group(Variable):
    value_type = Enum
    possible_values = AgeGroup
    default_value = AgeGroup.WORKING_AGE
    entity = Person
    label = u"Age group"
    definition_period = YEAR

    def formula(person, period, parameters):
        return select(
            [
                person("is_child", period),
                person("is_wa_adult", period),
                person("is_senior", period),
            ],
            [AgeGroup.CHILD, AgeGroup.WORKING_AGE, AgeGroup.SENIOR],
        )


class is_child(Variable):
    value_type = bool
    entity = Person
    label = u"Is a child"
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("age", period) < 18


class is_wa_adult(Variable):
    value_type = bool
    entity = Person
    label = u"Is a working-age adult"
    definition_period = YEAR

    def formula(person, period, parameters):
        age = person("age", period)
        return (age >= 18) & (age < 65)


class is_senior(Variable):
    value_type = bool
    entity = Person
    label = u"Is a senior"
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("age", period) >= 65


class is_citizen(Variable):
    value_type = bool
    entity = Person
    label = u"Is a U.S. citizen"
    definition_period = YEAR


class is_ccdf_home_based(Variable):
    value_type = bool
    default_value = False
    entity = Person
    label = u"Whether CCDF care is home-based versus center-based"
    definition_period = YEAR

    def formula(person, period, parameters):
        return (
            person("provider_type_group", period) != ProviderTypeGroup.DCC_SACC
        )


class CCDFAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOLER = "Preschooler"
    SCHOOL_AGE = "School age"


class ccdf_age_group(Variable):
    value_type = Enum
    possible_values = CCDFAgeGroup
    default_value = CCDFAgeGroup.INFANT
    entity = Person
    label = u"CCDF age group"
    definition_period = YEAR

    reference = "https://ocfs.ny.gov/main/policies/external/ocfs_2019/LCM/19-OCFS-LCM-23.pdf"

    def formula(person, period, parameters):
        age = person("age", period)
        home_based = person("is_ccdf_home_based", period)
        return select(
            [
                ((age < 1.5) & ~home_based) | ((age < 2) & home_based),
                ((age < 2) & ~home_based) | ((age < 3) & home_based),
                age < 6,
                age < 13,
            ],
            [
                CCDFAgeGroup.INFANT,
                CCDFAgeGroup.TODDLER,
                CCDFAgeGroup.PRESCHOOLER,
                CCDFAgeGroup.SCHOOL_AGE,
            ],
        )


class ProviderTypeGroup(Enum):
    DCC_SACC = "Licenced/registered/permitted day care center; registered school-age child care"
    FDC_GFDC = (
        "Registered family day care homes; licensed group family day care"
    )
    LE_GC = "Legally exempt group child care programs"
    LE_STD = "Informal child care standard rate"
    LE_ENH = "Informal child care enhanced rate"


class provider_type_group(Variable):
    value_type = Enum
    possible_values = ProviderTypeGroup
    # DCC_SACC is most common among provider types
    default_value = ProviderTypeGroup.DCC_SACC
    entity = Person
    label = u"CCDF provider type group"
    definition_period = YEAR


class childcare_hours_per_week(Variable):
    value_type = float
    entity = Person
    label = u"Child care hours per week"
    definition_period = YEAR


class childcare_hours_per_day(Variable):
    value_type = float
    entity = Person
    label = u"Child care hours per day"
    definition_period = YEAR


class childcare_days_per_week(Variable):
    value_type = float
    entity = Person
    label = u"Child care days per week"
    definition_period = YEAR


class DurationOfCare(Enum):
    WEEKLY = "Weekly"
    DAILY = "Daily"
    PART_DAY = "Part-Day"
    HOURLY = "Hourly"


class duration_of_care(Variable):
    value_type = Enum
    possible_values = DurationOfCare
    default_value = DurationOfCare.WEEKLY
    entity = Person
    label = u"Child care duration of care"
    definition_period = YEAR

    reference = "https://ocfs.ny.gov/main/policies/external/ocfs_2019/LCM/19-OCFS-LCM-23.pdf#page=5"

    def formula(person, period):
        hours_per_day = person("childcare_hours_per_day", period)
        days_per_week = person("childcare_days_per_week", period)
        hours_per_week = hours_per_day * days_per_week
        return select(
            [
                hours_per_week >= 30,
                hours_per_day >= 6,
                hours_per_day >= 3,
                True,
            ],
            [
                DurationOfCare.WEEKLY,
                DurationOfCare.DAILY,
                DurationOfCare.PART_DAY,
                DurationOfCare.HOURLY,
            ],
        )
