from policyengine_us.model_api import *


class LACCAPAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    REGULAR = "Regular"


class la_ccap_age_group(Variable):
    value_type = Enum
    possible_values = LACCAPAgeGroup
    default_value = LACCAPAgeGroup.REGULAR
    entity = Person
    definition_period = YEAR
    label = "Louisiana CCAP child age group"
    reference = "https://www.louisianabelieves.com/docs/default-source/child-care-providers/ccap-rate-changes.pdf?sfvrsn=2f5d8d1f_10"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.la.ldoe.ccap.age_group
        age = person("age", period)
        return select(
            [age < p.infant_age_limit, age < p.toddler_age_limit],
            [LACCAPAgeGroup.INFANT, LACCAPAgeGroup.TODDLER],
            default=LACCAPAgeGroup.REGULAR,
        )
