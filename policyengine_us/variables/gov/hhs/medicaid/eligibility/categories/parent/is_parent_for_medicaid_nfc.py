from policyengine_us.model_api import *


class is_parent_for_medicaid_nfc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid parent non-financial criteria"
    definition_period = YEAR
    documentation = """
    Determines if a person meets the non-financial criteria for Medicaid
    parent eligibility.

    In expansion states: Any adult who is not a dependent and has dependents
    in their tax unit qualifies.

    In non-expansion states (Section 1931 states): The state requires a child
    to be "deprived of parental support" which typically means single-parent
    households only. Two-parent households generally do not qualify unless
    one parent is incapacitated or unemployed.

    References:
    - 42 USC 1396u-1 (Section 1931)
    - https://www.kff.org/medicaid/state-indicator/medicaid-income-eligibility-limits-for-parents/
    """

    def formula(person, period, parameters):
        is_dependent = person("is_tax_unit_dependent", period)
        has_dependent_in_tax_unit = (
            person.tax_unit("tax_unit_count_dependents", period) > 0
        )

        # Basic criteria: not a dependent AND has dependents
        meets_basic_criteria = ~is_dependent & has_dependent_in_tax_unit

        # Check if state requires deprivation (non-expansion states)
        state = person.household("state_code_str", period)
        p = parameters(period).gov.hhs.medicaid.eligibility.categories.parent
        requires_deprivation = p.requires_deprivation[state]

        # For states requiring deprivation, must be single parent
        is_single_parent = person("is_single_parent_household", period)
        requires_deprivation_bool = requires_deprivation.astype(bool)
        meets_deprivation = ~requires_deprivation_bool | is_single_parent

        return meets_basic_criteria & meets_deprivation
