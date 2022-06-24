from openfisca_us.model_api import *


class is_ssi_ineligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI-ineligible child"
    definition_period = YEAR

    def formula(person, period, parameters):
        abd = person("is_ssi_aged_blind_disabled", period)
        child = person("is_child", period)
        return ~abd & child
