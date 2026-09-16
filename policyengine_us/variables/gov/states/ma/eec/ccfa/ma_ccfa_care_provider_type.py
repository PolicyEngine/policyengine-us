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
    reference = "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download"

    def formula(person, period, parameters):
        # An input overrides this. Unset, the type follows the child's own age
        # category: the two center-based rate tables are keyed by it, and the
        # school-age table has no rate for a child under school age, so a
        # fixed school-age default paid $0 for every infant, toddler and
        # preschooler whose caller had not named a provider (policyengine-us
        # #9485). The center-based table is the one a reported child-care bill
        # prices, as in every other state's default.
        age_category = person("ma_ccfa_child_age_category", period)
        school_age = (
            age_category
            == age_category.possible_values.SCHOOL_AGE
        )
        return where(
            school_age,
            MassachusettsCCFACareProviderType.CENTER_BASED_CARE_SCHOOL_AGE,
            MassachusettsCCFACareProviderType.CENTER_BASED_CARE_EARLY_EDUCATION,
        )
