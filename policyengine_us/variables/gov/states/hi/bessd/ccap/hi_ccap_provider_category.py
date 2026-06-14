from policyengine_us.model_api import *


class HICCAPProviderCategory(Enum):
    # Provider TYPE / care setting only -- the infant/toddler vs older split is
    # derived separately from the child's age (hi_ccap_age_group). Members
    # mirror the Exhibit I rate table (HAR 17-798.3, eff 2020-01-02), with each
    # infant/toddler + older row pair collapsed into one provider type. The
    # last two members are the before/after-school rows that use the separate
    # before_after hours-tier band scheme.
    LICENSED_CENTER_OR_GROUP_HOME = "Licensed center or group child care home"
    ACCREDITED_CENTER = "NAEYC/NECPA/Hawaiian-medium accredited center-based"
    NAFCC_ACCREDITED_FAMILY = "NAFCC accredited family child care home"
    REGISTERED_FAMILY = "Registered family child care home"
    LEGALLY_EXEMPT = "Legally exempt relative/non-relative/center"
    LICENSED_SCHOOL_AGE_INTERSESSION_SUMMER = "Licensed school-age intersession/summer"
    LICENSED_BEFORE_AFTER_SCHOOL = "Licensed before/after school"
    EXEMPT_BEFORE_AFTER_SCHOOL = "Legally exempt before/after school"


class hi_ccap_provider_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = HICCAPProviderCategory
    default_value = HICCAPProviderCategory.LICENSED_CENTER_OR_GROUP_HOME
    definition_period = MONTH
    label = "Hawaii CCAP provider category"
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/bessd/files/2021/09/CHAPTER-17-798.3-Child-Care-Payments.pdf#page=71"
