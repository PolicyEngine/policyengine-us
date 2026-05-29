from policyengine_us.model_api import *


class is_medicaid_slcsp_dependent_child(Variable):
    value_type = bool
    entity = Person
    label = "Person is a dependent child for Medicaid SLCSP cost indexing"
    definition_period = YEAR
    documentation = (
        "Child definition for assigning Medicaid enrollees to ACA family tiers. "
        "Kept separate from is_aca_family_tier_dependent_child because that "
        "variable gates on pays_aca_premium, which is false for Medicaid "
        "enrollees and would classify them all as non-children."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.aca
        age = person("age", period)
        is_tax_dependent = person("is_tax_unit_dependent", period)
        state_code = person.household("state_code", period)
        in_ny = state_code == state_code.possible_values.NY
        # New York extends dependent-child status to tax dependents aged 26-29,
        # mirroring is_aca_ny_age_29_dependent_child (minus the premium gate).
        ny_age_29_child = (
            in_ny
            & is_tax_dependent
            & (age >= p.family_tier_dependent_child_age_threshold)
            & (age < p.ny_age_29_dependent_child_age_threshold)
        )
        return (
            (age <= p.slcsp.max_child_age)
            | (is_tax_dependent & (age < p.family_tier_dependent_child_age_threshold))
            | ny_age_29_child
        )
