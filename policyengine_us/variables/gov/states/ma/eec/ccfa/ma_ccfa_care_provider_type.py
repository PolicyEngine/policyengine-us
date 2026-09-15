from policyengine_us.model_api import *


class MassachusettsCCFACareProviderType(Enum):
    CENTER_BASED_CARE_EARLY_EDUCATION = "Center-Based Care Early Education"
    CENTER_BASED_CARE_SCHOOL_AGE = "Center-Based Care School Age"
    HEAD_START_PARTNER_AND_KINDERGARTEN = "Head Start Partner and Kindergarten"
    INFORMAL_CHILD_CARE = "Informal Child Care"
    FAMILY_CHILD_CARE = "Family Child Care"


class ma_ccfa_care_provider_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = MassachusettsCCFACareProviderType
    default_value = MassachusettsCCFACareProviderType.CENTER_BASED_CARE_SCHOOL_AGE
    definition_period = MONTH
    defined_for = StateCode.MA
    label = "Massachusetts Child Care Financial Assistance (CCFA) care provider type"
    reference = "https://www.mass.gov/doc/eecfy26-rate-increase-chart/download#page=1"

    def formula(person, period, parameters):
        # NOTE: The rate sheets split center-based care into an early education
        # table (infant, toddler, preschool) and a school-age table, so an
        # unspecified provider type follows the child's age category.
        age_category = person("ma_ccfa_child_age_category", period)
        is_school_age = age_category == age_category.possible_values.SCHOOL_AGE
        return where(
            is_school_age,
            MassachusettsCCFACareProviderType.CENTER_BASED_CARE_SCHOOL_AGE,
            MassachusettsCCFACareProviderType.CENTER_BASED_CARE_EARLY_EDUCATION,
        )
