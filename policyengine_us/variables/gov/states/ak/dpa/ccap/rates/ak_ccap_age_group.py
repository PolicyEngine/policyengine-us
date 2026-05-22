from policyengine_us.model_api import *


class AKCCAPAgeGroup(Enum):
    INFANT = "Infant (0 to 12 months)"
    TODDLER = "Toddler (13 to 35 months)"
    PRESCHOOL = "Preschool (36 to 59 months)"
    SCHOOL_AGE = "School Age (60+ months)"


class ak_ccap_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = AKCCAPAgeGroup
    default_value = AKCCAPAgeGroup.PRESCHOOL
    definition_period = MONTH
    label = "Alaska CCAP age group"
    defined_for = StateCode.AK
    reference = "https://health.alaska.gov/media/wsvhl3v3/ccap-rate-schedule.pdf#page=1"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ak.dpa.ccap.age_group
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        return p.months.calc(age_in_months)
