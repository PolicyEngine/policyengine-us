from openfisca_us.model_api import *


class is_ccdf_home_based(Variable):
    value_type = bool
    default_value = False
    entity = Person
    label = "Whether CCDF care is home-based versus center-based"
    definition_period = YEAR

    def formula(person, period, parameters):
        provider_type_group = person("childcare_provider_type_group", period)
        provider_type_groups = provider_type_group.possible_values
        return provider_type_group != provider_type_groups.DCC_SACC
