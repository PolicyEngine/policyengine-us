from policyengine_us.model_api import *


class WVCCAPChildAgeCategory(Enum):
    INFANT = "Infant (0-24 months)"
    TODDLER = "Toddler (25-36 months)"
    PRESCHOOL = "Preschool (37-59 months)"
    SCHOOL_AGE = "School Age (60+ months)"


class wv_ccap_child_age_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = WVCCAPChildAgeCategory
    default_value = WVCCAPChildAgeCategory.PRESCHOOL
    definition_period = MONTH
    label = "West Virginia CCAP child age category"
    defined_for = StateCode.WV
    reference = "https://bfa.wv.gov/media/6831/download?inline#page=1"

    def formula(person, period, parameters):
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        p = parameters(period).gov.states.wv.dhhr.ccap.age_group
        return p.months.calc(age_in_months)
