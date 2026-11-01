from policyengine_us.model_api import *


class is_father(Variable):
    value_type = bool
    entity = Person
    label = "Is a father"
    definition_period = YEAR

    def formula(person, period, parameters):
        # is_parent combines the child count with co-resident parent links.
        female = person("is_female", period)
        has_children = person("is_parent", period)
        return ~female & has_children
