from policyengine_us.model_api import *


class NHCCAPChildAgeCategory(Enum):
    INFANT = "Infant (0-17 months)"
    TODDLER = "Toddler (18-35 months)"
    PRESCHOOL = "Preschool (36-78 months)"
    SCHOOL_AGE = "School Age (79-155 months)"


class nh_ccap_child_age_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = NHCCAPChildAgeCategory
    default_value = NHCCAPChildAgeCategory.INFANT
    definition_period = MONTH
    defined_for = StateCode.NH
    label = "New Hampshire Child Care Scholarship Program child age category"
    reference = "https://www.law.cornell.edu/regulations/new-hampshire/N-H-Admin-Code-SS-He-C-6910.17"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nh.dhhs.ccap.age_category
        age_months = person("age", period.this_year) * MONTHS_IN_YEAR

        return select(
            [
                age_months < p.infant_max_months,
                age_months < p.toddler_max_months,
                age_months < p.preschool_max_months,
            ],
            [
                NHCCAPChildAgeCategory.INFANT,
                NHCCAPChildAgeCategory.TODDLER,
                NHCCAPChildAgeCategory.PRESCHOOL,
            ],
            default=NHCCAPChildAgeCategory.SCHOOL_AGE,
        )
