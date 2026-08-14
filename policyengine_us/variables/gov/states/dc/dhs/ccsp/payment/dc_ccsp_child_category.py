from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.dc.dhs.ccsp.payment.dc_ccsp_age_category import (
    DCCCSPAgeCategory,
)


class DCCCSPChildCategory(Enum):
    INFANT_AND_TODDLER = "Infant and Toddler"
    INFANT_AND_TODDLER_SPECIAL_NEEDS = "Infant and Toddler Special Needs"
    PRESCHOOL = "Preschool"
    PRESCHOOL_BEFORE_AND_AFTER = "Preschool Before and After"
    SCHOOL_AGE_BEFORE_AND_AFTER = "School-Age Before and After"
    SCHOOL_AGE_BEFORE_OR_AFTER = "School-Age Before or After"
    PRESCHOOL_AND_SCHOOL_AGE_SPECIAL_NEEDS = "Preschool and School-Age Special Needs"


class dc_ccsp_child_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = DCCCSPChildCategory
    default_value = DCCCSPChildCategory.PRESCHOOL
    label = "DC Child Care Subsidy Program (CCSP) child category"
    definition_period = MONTH
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/FY25%20Subsidy%20Reimbursement%20Rates%20English.pdf"

    def formula(person, period, parameters):
        # The reimbursement rate sheet fuses the age band with the service
        # authorized, so map the age category onto the rate row that the band
        # alone determines. Preschool and Preschool Before and After carry
        # identical rates in every column of every quality tier, and School-Age
        # Before and After matches School-Age Before or After on the full-time
        # traditional rate while also covering the extended day and
        # nontraditional columns that Before or After lacks.
        #
        # The two special needs rows, and the School-Age Before or After
        # part-time rate, depend on the service authorized rather than on the
        # child's age, so set this variable directly for those cases. Special
        # needs is deliberately not derived from is_disabled: the rate sheet
        # publishes no special needs row for child development homes, so a
        # disabled child at a home provider would be priced at zero.
        age_category = person("dc_ccsp_age_category", period)
        return select(
            [
                age_category == DCCCSPAgeCategory.INFANT_AND_TODDLER,
                age_category == DCCCSPAgeCategory.PRESCHOOL,
            ],
            [
                DCCCSPChildCategory.INFANT_AND_TODDLER,
                DCCCSPChildCategory.PRESCHOOL,
            ],
            default=DCCCSPChildCategory.SCHOOL_AGE_BEFORE_AND_AFTER,
        )
