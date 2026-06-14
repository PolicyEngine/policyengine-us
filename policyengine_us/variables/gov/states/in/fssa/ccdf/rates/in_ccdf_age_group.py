from policyengine_us.model_api import *


class INCCDFAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    THREE_TO_FIVE = "Three, four, or five years"
    KINDERGARTEN = "Kindergarten"
    SCHOOL_AGE_BEFORE_AFTER = "School age before and after"
    SCHOOL_AGE_OTHER = "School age all other"


class in_ccdf_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = INCCDFAgeGroup
    default_value = INCCDFAgeGroup.INFANT
    definition_period = MONTH
    defined_for = StateCode.IN
    label = "Indiana CCDF age group"
    reference = (
        "https://www.in.gov/fssa/carefinder/files/CCDF-Provider-Manual.pdf#page=11"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states["in"].fssa.ccdf.age_group
        age_months = person("age", period.this_year) * MONTHS_IN_YEAR
        # Kindergarten is "half-day kindergarten or a child six years of age,
        # but has not started school", and school age splits into before/after
        # and all other by care schedule, not age. We don't track half-day
        # vs full-day kindergarten enrollment or care schedule at the moment,
        # so we map age 6 to kindergarten, age 7+ to school age before/after,
        # and never derive school age all other.
        return select(
            [
                age_months < p.infant_max_months,
                age_months < p.toddler_max_months,
                age_months < p.preschool_max_months,
                age_months < p.kindergarten_max_months,
            ],
            [
                INCCDFAgeGroup.INFANT,
                INCCDFAgeGroup.TODDLER,
                INCCDFAgeGroup.THREE_TO_FIVE,
                INCCDFAgeGroup.KINDERGARTEN,
            ],
            default=INCCDFAgeGroup.SCHOOL_AGE_BEFORE_AFTER,
        )
