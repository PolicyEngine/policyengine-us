from policyengine_us.model_api import *


class child_index(Variable):
    value_type = int
    entity = Person
    label = "Index of child in household"
    definition_period = YEAR

    def formula(person, period, parameters):
        return (
            person.get_rank(
                person.household,
                -person("age", period),
                condition=person("is_child", period),
            )
            + 1
        )
