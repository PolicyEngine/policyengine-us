from policyengine_us.model_api import *


class is_single_parent_household(Variable):
    value_type = bool
    entity = Person
    label = (
        "Person is in a single-parent household" " (for Medicaid deprivation)"
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        filing_status = person.tax_unit("filing_status", period)
        is_head = person("is_tax_unit_head", period)
        has_dependents = (
            person.tax_unit("tax_unit_count_dependents", period) > 0
        )

        is_joint = filing_status == filing_status.possible_values.JOINT
        is_separate = filing_status == filing_status.possible_values.SEPARATE
        is_married_filing = is_joint | is_separate

        return ~is_married_filing & has_dependents & is_head
