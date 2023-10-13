from policyengine_us.model_api import *


class is_tax_unit_head_or_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Head or Spouse of tax unit"
    definition_period = YEAR

    def formula(person, period, parameters):
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        return head | spouse
