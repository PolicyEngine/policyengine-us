from policyengine_us.model_api import *


class NJCCAPAgeGroup(Enum):
    INFANT = "Infant (Birth to 17 Months)"
    INFANT_SN = "Infant with Special Needs"
    TODDLER = "Toddler (18 to 29 Months)"
    TODDLER_SN = "Toddler with Special Needs"
    PRESCHOOL = "Preschool (30 Months to 5 Years)"
    PRESCHOOL_SN = "Preschool with Special Needs"
    SCHOOL_AGE = "School Age (5 to 13 Years)"
    SCHOOL_AGE_SN = "School Age with Special Needs"


class nj_ccap_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = NJCCAPAgeGroup
    default_value = NJCCAPAgeGroup.PRESCHOOL
    definition_period = MONTH
    label = "New Jersey CCAP age group"
    defined_for = StateCode.NJ
    reference = "https://www.childcarenj.gov/ChildCareNJ/media/media_library/Max_CC_Payment_Rates.pdf#page=1"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.njdhs.ccap.age_group
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        base_group = p.months.calc(age_in_months)
        is_disabled = person("is_disabled", period.this_year)
        # base_group: 0=INFANT, 1=TODDLER, 2=PRESCHOOL, 3=SCHOOL_AGE
        # SN variants are at indices: 1=INFANT_SN, 3=TODDLER_SN, 5=PRESCHOOL_SN, 7=SCHOOL_AGE_SN
        # Standard variants at: 0=INFANT, 2=TODDLER, 4=PRESCHOOL, 6=SCHOOL_AGE
        standard_index = base_group * 2
        sn_index = standard_index + 1
        return where(is_disabled, sn_index, standard_index)
