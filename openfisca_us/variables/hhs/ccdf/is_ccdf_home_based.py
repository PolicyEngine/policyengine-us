from openfisca_us.model_api import *


class is_ccdf_home_based(Variable):
    value_type = bool
    default_value = False
    entity = Person
    label = u"Whether CCDF care is home-based versus center-based"
    definition_period = YEAR

    def formula(person, period, parameters):
        return (
            person("provider_type_group", period) != ProviderTypeGroup.DCC_SACC
        )
