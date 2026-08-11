from policyengine_us.model_api import *


class OKCCSHomeAgeGroup(Enum):
    MONTHS_0_TO_24 = "0 to 24 months"
    MONTHS_25_TO_48 = "25 to 48 months"
    MONTHS_49_TO_72 = "49 to 72 months"
    MONTHS_73_PLUS = "73 months to 13 years"


class ok_ccs_home_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = OKCCSHomeAgeGroup
    default_value = OKCCSHomeAgeGroup.MONTHS_73_PLUS
    definition_period = MONTH
    label = "Oklahoma Child Care Subsidy child care home rate age group"
    defined_for = StateCode.OK
    reference = "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-4-b.pdf#page=3"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ok.dhs.ccs.age_group
        age_months = person("age", period.this_year) * MONTHS_IN_YEAR
        # The bracket returns the OKCCSHomeAgeGroup enum index. Children 13
        # and older receive the 73 months to 13 years rate when eligible past
        # age 13 with a disability (Appendix C-4-B).
        return p.home.calc(age_months)
