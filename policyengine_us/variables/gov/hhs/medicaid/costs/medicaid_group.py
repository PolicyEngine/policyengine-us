from policyengine_us.model_api import *


class MedicaidGroup(Enum):
    CHILD = "Child"
    NON_EXPANSION_ADULT = "Non-Expansion Adult"
    EXPANSION_ADULT = "Expansion Adult"
    AGED_DISABLED = "Aged/Disabled"
    NONE = "None"


class medicaid_group(Variable):
    """Maps fine-grained Medicaid categories to broader spending groups
    Precedence order (highest → lowest):
    1. Disabled / SSI / medically‑needy → AGED_DISABLED
    2. Pregnant                       → NON_EXPANSION_ADULT
    3. Parent                         → NON_EXPANSION_ADULT
    4. Young adult (19–20)            → NON_EXPANSION_ADULT
    5. Expansion adult                → EXPANSION_ADULT
    6. Any child category             → CHILD
    """

    value_type = Enum
    possible_values = MedicaidGroup
    default_value = MedicaidGroup.NONE
    entity = Person
    label = "Medicaid spending group"
    definition_period = YEAR

    def formula(person, period, parameters):
        eligible = person("is_medicaid_eligible", period)

        cat = person("medicaid_category", period)
        cats = cat.possible_values

        # Disabled / SSI / medically-needy → AGED_DISABLED
        disabled = (
            (cat == cats.SSI_RECIPIENT)
            | person("is_ssi_recipient_for_medicaid", period)
            | person("is_optional_senior_or_disabled_for_medicaid", period)
        )

        # Pregnant OR Parent OR Young adult (19–20) → NON_EXPANSION_ADULT
        non_expansion_adult = (
            (cat == cats.PREGNANT)
            | (cat == cats.PARENT)
            | (cat == cats.YOUNG_ADULT)
        )

        # Expansion adult → EXPANSION_ADULT
        expansion_adult = cat == cats.ADULT

        # Any child category → CHILD
        child = (
            (cat == cats.INFANT)
            | (cat == cats.YOUNG_CHILD)
            | (cat == cats.OLDER_CHILD)
        )

        # Core mapping, in precedence order:
        return select(
            [~eligible, disabled, non_expansion_adult, expansion_adult, child],
            [
                MedicaidGroup.NONE,
                MedicaidGroup.AGED_DISABLED,
                MedicaidGroup.NON_EXPANSION_ADULT,
                MedicaidGroup.EXPANSION_ADULT,
                MedicaidGroup.CHILD,
            ],
            default=MedicaidGroup.NONE,
        )
