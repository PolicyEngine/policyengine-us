from policyengine_us.model_api import *


class aca_child_index(Variable):
    value_type = int
    entity = Person
    label = "Index of child in tax unit"
    definition_period = YEAR

    def formula(person, period, parameters):
        age = person("age", period)
        is_child = age <= parameters(period).gov.aca.max_child_age
        child_rank = person.get_rank(person.tax_unit, -age, condition=is_child)
        return where(is_child, child_rank + 1, 99)
