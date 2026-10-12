from policyengine_us.model_api import *


class UTCCAPAgeGroup(Enum):
    UNDER_TWO = "Under 2 years old"
    TWO_YEAR_OLD = "2 years old"
    THREE_YEAR_OLD = "3 years old"
    FOUR_YEAR_OLD = "4 years old"
    FIVE_YEAR_OLD = "5 years old"
    SCHOOL_AGE = "6 to 12 years old"


class ut_ccap_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = UTCCAPAgeGroup
    default_value = UTCCAPAgeGroup.SCHOOL_AGE
    definition_period = MONTH
    label = "Utah CCAP rate-table age group"
    defined_for = StateCode.UT
    reference = "https://jobs.utah.gov/occ/provider/table30824.pdf"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ut.dwf.ccap.rates
        # Table 3 publishes no band above age 12; special needs children ages
        # 13 to 17 (eligible under R986-700-702(5)(b)) fall in the school age
        # band.
        age = person("age", period.this_year)
        return p.age_group.calc(age)
