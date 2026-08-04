from policyengine_us.model_api import *


class HICCAPAgeGroup(Enum):
    INFANT_TODDLER = "Infant/toddler (under 36 months)"
    OLDER = "Preschool and older (36 months and over)"


class hi_ccap_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = HICCAPAgeGroup
    default_value = HICCAPAgeGroup.OLDER
    definition_period = MONTH
    label = "Hawaii CCAP child age group"
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/bessd/files/2021/09/CHAPTER-17-798.3-Child-Care-Payments.pdf#page=9"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.hi.bessd.ccap.age
        # HAR 17-798.3-2: an "infant and toddler center" serves children six
        # weeks to thirty-six months of age, so a child under 36 months gets
        # the infant/toddler Exhibit I rate.
        age_months = person("age", period.this_year) * MONTHS_IN_YEAR
        return select(
            [age_months < p.infant_toddler_max_months],
            [HICCAPAgeGroup.INFANT_TODDLER],
            default=HICCAPAgeGroup.OLDER,
        )
