from policyengine_us.model_api import *


class has_disabled_spouse(Variable):
    value_type = bool
    entity = Person
    label = "person's marriage partner in JOINT filing unit is disabled"
    definition_period = YEAR

    def formula(person, period, parameters):
        filing_status = person.tax_unit("filing_status", period)
        married = filing_status == filing_status.possible_values.JOINT
        head_disabled = person.tax_unit("head_is_disabled", period)
        spouse_disabled = person.tax_unit("spouse_is_disabled", period)
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        return married & (
            (is_head & spouse_disabled) | (is_spouse & head_disabled)
        )
