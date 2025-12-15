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
    default_value = (
        MassachusettsCCFACareProviderType.CENTER_BASED_CARE_SCHOOL_AGE
    )
    definition_period = MONTH
    defined_for = StateCode.MA
    label = "Massachusetts Child Care Financial Assistance (CCFA) care provider type"
    reference = "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download"
