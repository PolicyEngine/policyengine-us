from unicodedata import category
from policyengine_us.model_api import *


class MedicaidCategory(Enum):
    INFANT = "Infant"
    YOUNG_CHILD = "Young child"
    OLDER_CHILD = "Older child"
    YOUNG_ADULT = "Young adult"
    ADULT = "Adult"
    PARENT = "Parent"
    PREGNANT = "Pregnant"
    SSI_RECIPIENT = "SSI recipient"
    SENIOR_OR_DISABLED = "Senior or disabled"
    NONE = "None"


class medicaid_category(Variable):
    value_type = Enum
    possible_values = MedicaidCategory
    default_value = MedicaidCategory.NONE
    entity = Person
    label = "Medicaid category"
    definition_period = YEAR

    def formula(person, period, parameters):
        categories = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.covered

        variable_to_category = dict(
            is_infant_for_medicaid=MedicaidCategory.INFANT,
            is_young_child_for_medicaid=MedicaidCategory.YOUNG_CHILD,
            is_older_child_for_medicaid=MedicaidCategory.OLDER_CHILD,
            is_young_adult_for_medicaid=MedicaidCategory.YOUNG_ADULT,
            is_adult_for_medicaid=MedicaidCategory.ADULT,
            is_parent_for_medicaid=MedicaidCategory.PARENT,
            is_pregnant_for_medicaid=MedicaidCategory.PREGNANT,
            is_ssi_recipient_for_medicaid=MedicaidCategory.SSI_RECIPIENT,
            is_optional_senior_or_disabled_for_medicaid=MedicaidCategory.SENIOR_OR_DISABLED,
        )

        # Iterate in the order defined by the parameter file (covered.yaml)
        # to ensure correct precedence (e.g., pregnant before expansion adult)
        ordered_variables = [
            name for name in categories if name in variable_to_category
        ]

        return select(
            [person(variable, period) for variable in ordered_variables]
            + [True],
            [variable_to_category[variable] for variable in ordered_variables]
            + [MedicaidCategory.NONE],
        )
