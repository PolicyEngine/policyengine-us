from policyengine_us.model_api import *


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
        # The reimbursement rate sheet names three age bands, defined in
        # 5-A DCMR 199: infants and toddlers (under 36 months), preschoolers
        # (36 to 60 months), and school-age children (60 months and over,
        # who receive only out-of-school-time care).
        p = parameters(period).gov.states.dc.dhs.ccsp.child_category
        # monthly_age preserves the age in years at monthly granularity, so
        # read age over the year and scale it to months instead.
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        # Preschool and Preschool Before and After carry identical rates in
        # every column of every quality tier, so the plain preschool category
        # is the safe default. School-age Before and After matches School-Age
        # Before or After on the full-time traditional rate and covers the
        # extended and nontraditional columns that Before or After lacks.
        # The two special needs categories, and the school-age Before or After
        # part-time rate, depend on the service authorized rather than on the
        # child's age, so set this variable directly for those cases.
        return select(
            [
                age_in_months < p.infant_and_toddler_max,
                age_in_months < p.preschool_max,
            ],
            [
                DCCCSPChildCategory.INFANT_AND_TODDLER,
                DCCCSPChildCategory.PRESCHOOL,
            ],
            default=DCCCSPChildCategory.SCHOOL_AGE_BEFORE_AND_AFTER,
        )
