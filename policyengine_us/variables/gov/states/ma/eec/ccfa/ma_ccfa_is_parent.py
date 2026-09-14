from policyengine_us.model_api import *


class ma_ccfa_is_parent(Variable):
    value_type = bool
    entity = Person
    label = "Parent living with a child applying for Massachusetts CCFA"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/eec-ccfa-2026-04-income-eligible-consolidated-policies-may-6-2026/download#page=22"

    def formula(person, period, parameters):
        # Supported households consist of parents and their children.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        adult_or_parent = ~person("is_child", period) | person("is_parent", period)
        return head_or_spouse & adult_or_parent
