from policyengine_us.model_api import *


class ILCCAPChildAgeGroup(Enum):
    UNDER_TWO = "Under age two"
    AGE_TWO = "Age two"
    AGE_THREE_OR_OLDER = "Age three or older"


class il_ccap_child_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = ILCCAPChildAgeGroup
    default_value = ILCCAPChildAgeGroup.UNDER_TWO
    definition_period = MONTH
    label = "Illinois CCAP child age group"
    defined_for = StateCode.IL
    reference = "https://idec.illinois.gov/content/dam/soi/en/web/idec/documents/pages/ccap-for-providers/IL444-4343%20-%20Child%20Care%20Payment%20Rates%20for%20Child%20Care%20Providers%207.1.26.pdf#page=1"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap.rates.age_group
        age = person("monthly_age", period)
        return select(
            [
                age < p.age_two_minimum,
                (age >= p.age_two_minimum) & (age < p.age_three_or_older_minimum),
                age >= p.age_three_or_older_minimum,
            ],
            [
                ILCCAPChildAgeGroup.UNDER_TWO,
                ILCCAPChildAgeGroup.AGE_TWO,
                ILCCAPChildAgeGroup.AGE_THREE_OR_OLDER,
            ],
            default=ILCCAPChildAgeGroup.UNDER_TWO,
        )
