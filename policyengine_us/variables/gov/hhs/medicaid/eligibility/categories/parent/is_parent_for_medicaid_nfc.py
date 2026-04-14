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

        meets_basic_criteria = ~is_dependent & has_dependent_in_tax_unit

        state = person.household("state_code_str", period)
        p = parameters(period).gov.hhs.medicaid.eligibility.categories.parent
        requires_deprivation = p.requires_deprivation[state]

        is_single_parent = person("is_single_parent_household", period)
        requires_deprivation_bool = requires_deprivation.astype(bool)
        meets_deprivation = ~requires_deprivation_bool | is_single_parent

        return meets_basic_criteria & meets_deprivation
