from unicodedata import category
from openfisca_us.model_api import *


class MedicaidCategory(Enum):
    INFANT = "Infant"
    YOUNG_CHILD = "Young child"
    OLDER_CHILD = "Older child"
    YOUNG_ADULT = "Young adult"
    ADULT = "Adult"
    PARENT = "Parent"
    PREGNANT = "Pregnant"
    SSI_RECIPIENT = "SSI recipient"
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
        )

        # Ensure parametric reforms to the list of categories prevent those
        # categories from being selected.

        variable_to_category = {
            name: category
            for name, category in variable_to_category.items()
            if name in categories
        }

        return select(
            [
                person(variable, period)
                for variable in variable_to_category.keys()
            ]
            + [True],
            list(variable_to_category.values()) + [MedicaidCategory.NONE],
        )
