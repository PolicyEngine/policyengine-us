from policyengine_us.model_api import *


class HICCAPProviderCategory(Enum):
    # Members mirror the rows of the Exhibit I rate table (HAR 17-798.2-12).
    # Order matters: the rates.yaml breakdown is keyed by this enum, and the
    # last two members are the before/after-school rows that use the
    # separate before_after hours-tier band scheme.
    CENTER_INFANT_TODDLER = "Center-based infant/toddler"
    ACCREDITED_CENTER = "Accredited center-based"
    LICENSED_CENTER_OR_GROUP_HOME = "Licensed center or group child care home"
    LICENSED_FAMILY_INFANT_TODDLER = "Licensed family child care home infant/toddler"
    LICENSED_FAMILY = "Licensed family child care home"
    EXEMPT_INFANT_TODDLER = "License-exempt infant/toddler"
    EXEMPT = "License-exempt"
    LICENSED_BEFORE_AFTER_SCHOOL = "Licensed before/after school"
    EXEMPT_BEFORE_AFTER_SCHOOL = "License-exempt before/after school"


class hi_ccap_provider_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = HICCAPProviderCategory
    default_value = HICCAPProviderCategory.LICENSED_CENTER_OR_GROUP_HOME
    definition_period = MONTH
    label = "Hawaii CCAP provider category"
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/wp-content/uploads/2018/04/Child-Care-Rate-Table-2017-08-01.pdf"
