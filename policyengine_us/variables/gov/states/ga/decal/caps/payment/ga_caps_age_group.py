from policyengine_us.model_api import *


class GACAPSAgeGroup(Enum):
    INFANT = "Infant"
    TODDLER = "Toddler"
    PRESCHOOL = "Preschool"
    SCHOOL_AGE = "School Age"


class ga_caps_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = GACAPSAgeGroup
    default_value = GACAPSAgeGroup.PRESCHOOL
    definition_period = MONTH
    defined_for = "ga_caps_eligible_child"
    label = "Georgia CAPS child age group"
    reference = "https://caps.decal.ga.gov/assets/downloads/CAPS/AppendixC-CAPS%20Reimbursement%20Rates.pdf#page=1"

    def formula(person, period, parameters):
        age = person("age", period.this_year)
        p = parameters(period).gov.states.ga.decal.caps.age_group
        return select(
            [
                age < p.toddler_min,
                age < p.preschool_min,
                age < p.school_age_min,
            ],
            [
                GACAPSAgeGroup.INFANT,
                GACAPSAgeGroup.TODDLER,
                GACAPSAgeGroup.PRESCHOOL,
            ],
            default=GACAPSAgeGroup.SCHOOL_AGE,
        )
