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
    SENIOR_OR_DISABLED = " Senior or disabled"
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

        # Federal law requires mandatory categorically needy groups to be
        # evaluated before optional groups. The ACA rules under 42 CFR 435.119
        # prohibit enrollment in the Adult expansion group if the individual
        # is eligible for a different mandatory coverage group.
        #
        # Hierarchy based on 42 CFR Part 435:
        # - Subpart B: mandatory coverage groups
        # - Section 435.119: adult expansion "not otherwise eligible" requirement
        #
        # References:
        # - https://www.law.cornell.edu/cfr/text/42/435.119
        # - https://www.law.cornell.edu/cfr/text/42/part-435/subpart-B
        variable_to_category = dict(
            # 1. SSI recipients - non-MAGI pathway
            #    Automatic Medicaid eligibility in most states (42 CFR 435.120-138)
            is_ssi_recipient_for_medicaid=MedicaidCategory.SSI_RECIPIENT,
            # 2. Children - mandatory MAGI groups (42 CFR 435.118)
            is_infant_for_medicaid=MedicaidCategory.INFANT,
            is_young_child_for_medicaid=MedicaidCategory.YOUNG_CHILD,
            is_older_child_for_medicaid=MedicaidCategory.OLDER_CHILD,
            # 3. Pregnant women - mandatory MAGI (42 CFR 435.116)
            #    Evaluated before parents per state hierarchy guidance
            is_pregnant_for_medicaid=MedicaidCategory.PREGNANT,
            # 4. Parents/caretaker relatives - mandatory MAGI (42 CFR 435.110)
            is_parent_for_medicaid=MedicaidCategory.PARENT,
            # 5. Young adults (19-20) - optional state coverage
            is_young_adult_for_medicaid=MedicaidCategory.YOUNG_ADULT,
            # 6. Adult expansion - mandatory but requires "not otherwise eligible"
            #    per 42 CFR 435.119, so evaluated last among mandatory groups
            is_adult_for_medicaid=MedicaidCategory.ADULT,
            # 7. Optional aged/blind/disabled pathway (non-SSI)
            is_optional_senior_or_disabled_for_medicaid=MedicaidCategory.SENIOR_OR_DISABLED,
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
            ],
            list(variable_to_category.values()),
            default=MedicaidCategory.NONE,
        )
