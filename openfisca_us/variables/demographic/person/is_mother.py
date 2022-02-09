from openfisca_us.model_api import *


class is_mother(Variable):
    value_type = bool
    entity = Person
    label = "Is a mother"
    definition_period = YEAR

    def formula(person, period, parameters):
        # In the absence of relationship identifiers, breastfeeding is the
        # only indicator of motherhood.
        return person("is_breastfeeding", period)
