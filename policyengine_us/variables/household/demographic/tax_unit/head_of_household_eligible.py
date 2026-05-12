from policyengine_us.model_api import *


class head_of_household_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Qualifies for head of household filing status"
    reference = "https://www.law.cornell.edu/uscode/text/26/2#b"

    def formula(tax_unit, period, parameters):
        married = tax_unit("tax_unit_married", period)
        person = tax_unit.members
        # IRC 7703(b) "considered unmarried" applies to the taxpayer (head or
        # spouse), not to dependents. A separated dependent must not trigger
        # the 7703(b) child-only qualifying-person path.
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_separated = tax_unit.any(is_head_or_spouse & person("is_separated", period))
        # Qualifying children and permanently disabled always count
        is_qualifying_child = person("is_qualifying_child_dependent", period)
        is_disabled_dependent = person(
            "is_permanently_and_totally_disabled", period
        ) & person("is_tax_unit_dependent", period)
        # Qualifying relatives only count if related per IRC 2(b)(3)
        is_qualifying_relative = person("is_qualifying_relative_dependent", period)
        is_related = person("is_related_to_head_or_spouse", period)
        is_hoh_qualifying = (
            is_qualifying_child
            | is_disabled_dependent
            | (is_qualifying_relative & is_related)
        )
        has_qualifying_person = tax_unit.sum(is_hoh_qualifying) > 0
        # IRC 7703(b) treated-unmarried status supports HoH only through the
        # child-abode path, not the broader qualifying-relative route.
        treated_unmarried_qualifies = tax_unit.sum(is_qualifying_child) > 0
        surviving_spouse = tax_unit("surviving_spouse_eligible", period)
        unmarried_qualifies = has_qualifying_person & ~married & ~is_separated
        separated_qualifies = treated_unmarried_qualifies & is_separated
        return (unmarried_qualifies | separated_qualifies) & ~surviving_spouse
