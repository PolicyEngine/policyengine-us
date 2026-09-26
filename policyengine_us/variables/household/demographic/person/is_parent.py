from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    linked_child_count,
)


class is_parent(Variable):
    value_type = bool
    entity = Person
    label = "Is a parent"
    definition_period = YEAR

    def formula(person, period, parameters):
        # A person is a parent when their own child count is positive or when
        # a co-resident person's parent id names them. Neither source erases
        # the other, so links for one family never remove another family's
        # parent. Without ids this is the child count alone.
        return (person("own_children_in_household", period) > 0) | (
            linked_child_count(person, period) > 0
        )
