from policyengine_us.model_api import *


class HICCAPProviderCategory(Enum):
    # Members mirror the rows of the Exhibit I rate table (HAR 17-798.3,
    # effective 2020-01-02). Order matters: the rates.yaml breakdown is keyed
    # by this enum, and the last two members are the before/after-school rows
    # that use the separate before_after hours-tier band scheme.
    LICENSED_CENTER_INFANT_TODDLER = "Licensed center-based infant/toddler"
    ACCREDITED_CENTER = "NAEYC/NECPA/Hawaiian-medium accredited center-based"
    LICENSED_CENTER_OR_GROUP_HOME = "Licensed center or group child care home"
    NAFCC_ACCREDITED_FAMILY_INFANT_TODDLER = (
        "NAFCC accredited family child care home infant/toddler"
    )
    NAFCC_ACCREDITED_FAMILY = "NAFCC accredited family child care home"
    REGISTERED_FAMILY_INFANT_TODDLER = (
        "Registered family child care home infant/toddler"
    )
    REGISTERED_FAMILY = "Registered family child care home"
    EXEMPT_INFANT_TODDLER = "Legally exempt relative/non-relative infant/toddler"
    EXEMPT = "Legally exempt relative, non-relative, and center-based"
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
