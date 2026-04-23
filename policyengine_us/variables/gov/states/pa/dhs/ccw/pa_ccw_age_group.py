from policyengine_us.model_api import *


class PACCWAgeGroup(Enum):
    INFANT = "Infant"
    YOUNG_TODDLER = "Young Toddler"
    OLD_TODDLER = "Old Toddler"
    PRE_SCHOOL = "Pre-School"
    SCHOOL_AGE = "School Age"


class pa_ccw_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = PACCWAgeGroup
    default_value = PACCWAgeGroup.PRE_SCHOOL
    definition_period = MONTH
    label = "Pennsylvania CCW MCCA age group"
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=4"

    def formula(person, period, parameters):
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        p = parameters(period).gov.states.pa.dhs.ccw.age_group
        return p.months.calc(age_in_months)
