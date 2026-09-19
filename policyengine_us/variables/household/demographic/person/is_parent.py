from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
)


class is_parent(Variable):
    value_type = bool
    entity = Person
    label = "Is a parent"
    definition_period = YEAR

    def formula(person, period, parameters):
        has_parent_ids = (person("parent_1_id", period) != 0) | (
            person("parent_2_id", period) != 0
        )
        first, second = co_resident_parent_indices(person, period)
        parents = np.concatenate((first, second))
        linked_parent = np.bincount(parents[parents >= 0], minlength=person.count) > 0
        return where(
            person.household.any(has_parent_ids),
            linked_parent,
            person("own_children_in_household", period) > 0,
        )
