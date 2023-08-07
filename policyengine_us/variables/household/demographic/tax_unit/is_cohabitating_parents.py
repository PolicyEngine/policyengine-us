from policyengine_us.model_api import *


class is_cohabitating_parent(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Is a cohabitating parent"
    definition_period = YEAR

    def formula(person, period, parameters):
        return tax_unit("cohabitating_parent", period) = person("is_grandparent", period)
