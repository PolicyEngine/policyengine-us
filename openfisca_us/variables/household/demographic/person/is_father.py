from openfisca_us.model_api import *


class is_father(Variable):
    value_type = bool
    entity = Person
    label = "Is a father"
    definition_period = YEAR

    def formula(person, period, parameters):
        # In the absence of relationship identifiers, check if the person is
        # male and has some children in their own household (provided in the
        # CPS).
        female = person("is_female", period)
        has_children = person("own_children_in_household", period) > 0
        return ~female & has_children
