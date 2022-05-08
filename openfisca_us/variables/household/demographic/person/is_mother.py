from openfisca_us.model_api import *


class is_mother(Variable):
    value_type = bool
    entity = Person
    label = "Is a mother"
    definition_period = YEAR

    def formula(person, period, parameters):
        # In the absence of relationship identifiers, breastfeeding is the
        # only indicator of motherhood.
        breastfeeding = person("is_breastfeeding", period)
        adult_female = person("is_female", period) & person("is_adult", period)
        has_children = person.spm_unit.any(person("is_child", period))
        return breastfeeding | (adult_female & has_children)
