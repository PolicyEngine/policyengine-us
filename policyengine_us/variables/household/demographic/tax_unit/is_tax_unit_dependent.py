from policyengine_us.model_api import *


class is_tax_unit_dependent(Variable):
    value_type = bool
    entity = Person
    label = "Is a dependent in the tax unit"
    definition_period = YEAR
    documentation = (
        "Whether this person is a dependent in their tax unit. Tax-unit membership "
        "alone does not establish dependency. Without explicit roles, a member aged "
        "18 or older can be inferred as the spouse. Supplying filing_status alone, "
        "including SINGLE or HEAD_OF_HOUSEHOLD, does not prevent spouse inference. "
        "Supply is_tax_unit_dependent for the dependent, or provide complete "
        "tax_unit_role_input roles for every tax-unit member."
    )

    def formula(person, period, parameters):
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        return ~head & ~spouse
