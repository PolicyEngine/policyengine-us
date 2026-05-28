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
        return (age <= p.slcsp.max_child_age) | (
            is_tax_dependent & (age < p.family_tier_dependent_child_age_threshold)
        )
