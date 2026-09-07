from policyengine_us.model_api import *


class is_mother(Variable):
    value_type = bool
    entity = Person
    label = "Is a mother"
    definition_period = YEAR

    def formula(person, period, parameters):
        # is_parent uses co-resident parent links when available and otherwise
        # the child count. Breastfeeding independently identifies a mother.
        female = person("is_female", period)
        has_children = person("is_parent", period)
        breastfeeding = person("is_breastfeeding", period)
        return breastfeeding | (female & has_children)
