from policyengine_us.model_api import *


class FLSRCareLevel(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    TWO_YEAR_OLD = "2 Year Old"
    PRESCHOOL_3 = "Preschool 3"
    PRESCHOOL_4 = "Preschool 4"
    PRESCHOOL_5 = "Preschool 5"
    SCHOOL_AGE = "School Age"


class fl_sr_care_level(Variable):
    value_type = Enum
    possible_values = FLSRCareLevel
    default_value = FLSRCareLevel.SCHOOL_AGE
    entity = Person
    definition_period = MONTH
    label = "Florida School Readiness care level"
    defined_for = StateCode.FL
    reference = "https://www.flrules.org/gateway/RuleNo.asp?id=6M-4.500"

    def formula(person, period, parameters):
        # The reimbursement schedule's care levels are single-year age bands
        # (Infant <1, Toddler 1, 2 Year Old 2, Preschool 3/4/5 = ages 3/4/5,
        # School Age 6+). The bracket parameter returns the enum index by age.
        age = person("age", period.this_year)
        p = parameters(period).gov.states.fl.doe.sr.rates.care_level_age
        return p.calc(age)
