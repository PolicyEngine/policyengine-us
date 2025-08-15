from policyengine_us.model_api import *


class MassachusettsCCFAChildAgeCategory(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School Age"


class ma_ccfa_child_age_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = MassachusettsCCFAChildAgeCategory
    default_value = MassachusettsCCFAChildAgeCategory.INFANT
    definition_period = MONTH
    defined_for = StateCode.MA
    label = "Massachusetts Child Care Financial Assistance (CCFA) child age category"
    reference = "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download"
