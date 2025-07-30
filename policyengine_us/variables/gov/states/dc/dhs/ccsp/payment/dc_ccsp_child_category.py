from policyengine_us.model_api import *


class DCCCSPChildCategory(Enum):
    INFANT_AND_TODDLER = "Infant and Toddler"
    INFANT_AND_TODDLER_SPECIAL_NEEDS = "Infant and Toddler Special Needs"
    PRESCHOOL = "Preschool"
    PRESCHOOL_BEFORE_AND_AFTER = "Preschool Before and After"
    SCHOOL_AGE_BEFORE_AND_AFTER = "School-Age Before and After"
    SCHOOL_AGE_BEFORE_OR_AFTER = "School-Age Before or After"
    PRESCHOOL_AND_SCHOOL_AGE_SPECIAL_NEEDS = (
        "Preschool and School-Age Special Needs"
    )


class dc_ccsp_child_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = DCCCSPChildCategory
    default_value = DCCCSPChildCategory.PRESCHOOL
    label = "DC Child Care Subsidy Program (CCSP) child category"
    definition_period = MONTH
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/FY25%20Subsidy%20Reimbursement%20Rates%20English.pdf"
