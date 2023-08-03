from policyengine_us.model_api import *


class AgeGroup(Enum):
    CHILD = "Child"
    WORKING_AGE = "Working-age"
    SENIOR = "Senior"


class age_group(Variable):
    value_type = Enum
    possible_values = AgeGroup
    default_value = AgeGroup.WORKING_AGE
    entity = Person
    label = "Age group"
    definition_period = YEAR

    def formula(person, period, parameters):
        return select(
            [
                person("is_child", period),
                person("is_wa_adult", period),
                person("is_senior", period),
            ],
            [AgeGroup.CHILD, AgeGroup.WORKING_AGE, AgeGroup.SENIOR],
        )
