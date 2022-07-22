from openfisca_us.model_api import *


class is_mother(Variable):
    value_type = bool
    entity = Person
    label = "Is a mother"
    definition_period = YEAR

    def formula(person, period, parameters):
        # In the absence of relationship identifiers, check one of two
        # conditions:
        # 1. The person is female and has some children in their own household
        #    (provided in the CPS).
        # 2. Breastfeeding (user-input).
        female = person("is_female", period)
        has_children = person("own_children_in_household", period) > 0
        breastfeeding = person("is_breastfeeding", period)
        return breastfeeding | (female & has_children)
