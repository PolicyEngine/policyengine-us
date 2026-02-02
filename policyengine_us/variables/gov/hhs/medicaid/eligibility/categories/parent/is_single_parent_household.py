from policyengine_us.model_api import *


class is_single_parent_household(Variable):
    value_type = bool
    entity = Person
    label = "Person is in a single-parent household (for Medicaid deprivation)"
    definition_period = YEAR
    documentation = """
    Determines if a person is a single parent for purposes of Medicaid
    Section 1931 eligibility in non-expansion states.

    Under Section 1931, states that did not expand Medicaid require a child
    to be "deprived of parental support" for the parent to qualify. This
    typically means single-parent households qualify, while two-parent
    households generally do not (unless one parent is incapacitated/unemployed).

    This variable returns True for:
    - Head of Household filers with dependents (clearly single parents)
    - Single filers with dependents

    It returns False for:
    - Joint filers (married couples)
    - Married filing separately (still married)
    """

    def formula(person, period, parameters):
        filing_status = person.tax_unit("filing_status", period)
        is_head = person("is_tax_unit_head", period)
        has_dependents = (
            person.tax_unit("tax_unit_count_dependents", period) > 0
        )

        # Single parent = not married AND has dependents AND is the head
        is_joint = filing_status == filing_status.possible_values.JOINT
        is_separate = filing_status == filing_status.possible_values.SEPARATE
        is_married_filing = is_joint | is_separate

        return ~is_married_filing & has_dependents & is_head
