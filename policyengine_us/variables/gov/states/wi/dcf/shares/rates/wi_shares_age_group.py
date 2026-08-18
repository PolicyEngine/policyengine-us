from policyengine_us.model_api import *


class WISharesAgeGroup(Enum):
    AGE_0_THROUGH_1 = "0 through 1 years"
    AGE_2_THROUGH_3 = "2 through 3 years"
    AGE_4_THROUGH_5 = "4 through 5 years"
    AGE_6_AND_OLDER = "6 years and older"


class wi_shares_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = WISharesAgeGroup
    default_value = WISharesAgeGroup.AGE_6_AND_OLDER
    definition_period = MONTH
    label = "Wisconsin Shares rate-table age group"
    defined_for = StateCode.WI
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=156",
        "https://dcf.wisconsin.gov/files/wishares/pdf/max-rates-statewide.pdf#page=26",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dcf.shares
        age = person("age", period.this_year)
        # The bracket amounts are the indices of the enum members above.
        return p.age_group.calc(age)
