from policyengine_us.model_api import *


class aca_child_index(Variable):
    value_type = int
    entity = Person
    label = "Index of child in tax unit (1 = oldest)"
    definition_period = YEAR

    def formula(person, period, parameters):
        age = person("age", period)
        is_child = age <= parameters(period).gov.aca.slcsp.max_child_age
        child_rank = person.get_rank(person.tax_unit, -age, condition=is_child)
        # child_rank of 0 ==> oldest; ties broken by order in the tax unit
        ADULT_VALUE = 99
        return where(is_child, child_rank + 1, ADULT_VALUE)
