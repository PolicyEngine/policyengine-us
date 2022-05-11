from openfisca_us.model_api import *


class MedicaidPersonType(Enum):
    ADULT_WITHOUT_DEPENDENT = "Adult without dependent"
    ADULT_WITH_DEPENDENT = "Adult with dependent"
    PREGNANT = "Pregnant adult"
    CHILD_AGE_0 = "Child age 0"
    CHILD_AGE_1_5 = "Child age 1 to 5"
    CHILD_AGE_6_17 = "Child age 6 to 17"
    CHILD_AGE_18_20 = "Adult under 21 (covered as child)"
    AGED_BLIND_DISABLED = "Aged, blind, or disabled"


class medicaid_person_type(Variable):
    value_type = Enum
    possible_values = MedicaidPersonType
    default_value = MedicaidPersonType.ADULT_WITHOUT_DEPENDENT
    entity = Person
    definition_period = YEAR
    label = "Medicaid person type"
    documentation = "Person type for Medicaid"

    def formula(person, period, parameters):
        ma = parameters(period).hhs.medicaid
        # Get the person's age.
        age = person("age", period)
        # Get the existence of dependents, as defined by people 18 or younger.
        has_dependents = person.spm_unit.any(
            age < ma.dependent_age
        )
        under_21_qualifies = ma.under_21_qualifies_as_child
        state = person.household("state_code_str", period)
        state_has_under_21_child_category = under_21_qualifies[state] > 0
        is_pregnant = person("is_pregnant", period)
        days_postpartum = person("count_days_postpartum", period)
        max_postpartum_days = ma.postpartum_coverage[state]
        is_covered_as_pregnant = is_pregnant | (
            days_postpartum < max_postpartum_days
        )
        qualifies_as_disabled = person(
            "meets_medicaid_disabled_criteria", period
        )
        return select(
            [
                is_covered_as_pregnant,
                qualifies_as_disabled,
                age == 0,
                age < 6,
                age < 18,
                (age < 21) & state_has_under_21_child_category,
                has_dependents,
                True,
            ],
            [
                MedicaidPersonType.PREGNANT,
                MedicaidPersonType.AGED_BLIND_DISABLED,
                MedicaidPersonType.CHILD_AGE_0,
                MedicaidPersonType.CHILD_AGE_1_5,
                MedicaidPersonType.CHILD_AGE_6_17,
                MedicaidPersonType.CHILD_AGE_18_20,
                MedicaidPersonType.ADULT_WITH_DEPENDENT,
                MedicaidPersonType.ADULT_WITHOUT_DEPENDENT,
            ],
        )
