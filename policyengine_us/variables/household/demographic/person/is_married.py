from policyengine_us.model_api import *


class is_married(Variable):
    value_type = bool
    entity = Family
    label = "Married"
    documentation = "Whether the adults in this family are married."
    definition_period = YEAR

    def formula(family, period, parameters):
        person = family.members
        return family.any(person("is_tax_unit_spouse", period))
