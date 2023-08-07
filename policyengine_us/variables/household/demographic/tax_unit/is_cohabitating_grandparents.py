from policyengine_us.model_api import *


class is_cohabitating_grandparent(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Is a cohabitating grandparent"
    definition_period = YEAR

    def formula(person, period, parameters):
        return tax_unit("cohabitating_grandparent", period) = person("is_grandgrandparent", period)
