from policyengine_us.model_api import *


class IACCAAgeGroup(Enum):
    INFANT_TODDLER = "Infant and Toddler"
    INFANT_TODDLER_SN = "Infant and Toddler with Special Needs"
    PRESCHOOL = "Preschool"
    PRESCHOOL_SN = "Preschool with Special Needs"
    SCHOOL_AGE = "School Age"
    SCHOOL_AGE_SN = "School Age with Special Needs"


class ia_cca_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = IACCAAgeGroup
    default_value = IACCAAgeGroup.PRESCHOOL
    definition_period = MONTH
    label = "Iowa CCA child care rate age group"
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=15"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.hhs.cca.age_group
        # `age` is YEAR-defined; read the annual value inside this monthly
        # formula. The bracket returns the base group from the child's age
        # in years: 0 = infant and toddler (under 3), 1 = preschool
        # (3 to school age), 2 = school age (5 and older).
        age = person("age", period.this_year)
        base_group = p.age_group.calc(age)
        # Iowa pays a higher special-needs rate for a child who receives
        # special-needs care; we use the disability flag as the proxy. The
        # special-needs variant of each base group sits at the next enum
        # index (0=INFANT_TODDLER, 1=INFANT_TODDLER_SN, 2=PRESCHOOL,
        # 3=PRESCHOOL_SN, 4=SCHOOL_AGE, 5=SCHOOL_AGE_SN).
        is_disabled = person("is_disabled", period.this_year)
        standard_index = base_group * 2
        sn_index = standard_index + 1
        return where(is_disabled, sn_index, standard_index)
