from policyengine_us.model_api import *


class MedicaidGroup(Enum):
    """High‑level eligibility groups for per‑capita cost analysis."""

    CHILD = "CHILD"
    NON_EXPANSION_ADULT = "NON_EXPANSION_ADULT"
    EXPANSION_ADULT = "EXPANSION_ADULT"
    AGED_DISABLED = "AGED_DISABLED"
    NONE = "NONE"  # fallback for ineligible or uncategorised persons


class medicaid_group(Variable):
    """Maps fine‑grained Medicaid eligibility categories to broader spending groups.

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
        if not person("is_medicaid_eligible", period):
            return MedicaidGroup.NONE
        
        cat = person("medicaid_category", period)

        # --- Highest‑precedence: disabled / SSI / medically‑needy ---
        disabled = (
            (cat == cat.possible_values.SSI_RECIPIENT)
            | person("is_ssi_recipient_for_medicaid", period)
            | person("is_optional_senior_or_disabled_for_medicaid", period)
        )

        # TODO: add `is_medically_needy_for_medicaid` when that variable exists

        pregnant = cat == cat.possible_values.PREGNANT
        parent = cat == cat.possible_values.PARENT
        young_adult = cat == cat.possible_values.YOUNG_ADULT
        expansion_adult = cat == cat.possible_values.ADULT
        child = (
            (cat == cat.possible_values.INFANT)
            | (cat == cat.possible_values.YOUNG_CHILD)
            | (cat == cat.possible_values.OLDER_CHILD)
        )

        return select(
            [
                disabled,
                pregnant,
                parent,
                young_adult,
                expansion_adult,
                child,
            ],
            [
                MedicaidGroup.AGED_DISABLED,
                MedicaidGroup.NON_EXPANSION_ADULT,
                MedicaidGroup.NON_EXPANSION_ADULT,
                MedicaidGroup.NON_EXPANSION_ADULT,
                MedicaidGroup.EXPANSION_ADULT,
                MedicaidGroup.CHILD,
            ],
            default=MedicaidGroup.NONE,
        )
