from policyengine_us.model_api import *


class is_parent_for_medicaid_nfc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid parent non-financial criteria"
    definition_period = YEAR

    def formula(person, period, parameters):
        is_dependent = person("is_tax_unit_dependent", period)
        has_dependent_in_tax_unit = (
            person.tax_unit("tax_unit_count_dependents", period) > 0
        )
        return ~is_dependent & has_dependent_in_tax_unit
