from policyengine_us.model_api import *
from policyengine_us.variables.gov.aca.slspc.slcsp_family_tier_category import (
    FamilyTierCategory,
)


class basic_health_program_family_tier_category(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = FamilyTierCategory
    default_value = FamilyTierCategory.INDIVIDUAL_AGE_RATED
    label = "Basic Health Program family tier category"
    definition_period = MONTH
    defined_for = "slcsp_family_tier_applies"

    def formula(tax_unit, period, parameters):
        state_code = tax_unit.household("state_code_str", period)

        person = tax_unit.members
        enrolled = person("basic_health_program_enrolled", period)
        dependent_child = person(
            "basic_health_program_family_tier_dependent_child", period
        )
        non_dependent_adult_count = tax_unit.sum(enrolled & ~dependent_child)
        anchored_child_count = tax_unit.sum(dependent_child)

        under_child_only_age = (
            person("monthly_age", period)
            <= parameters(period).gov.aca.slcsp.max_child_age
        )
        child_only_child = enrolled & under_child_only_age
        unanchored_adult_count = tax_unit.sum(enrolled & ~child_only_child)
        unanchored_child_count = tax_unit.sum(child_only_child)
        has_adult_anchor = non_dependent_adult_count > 0
        eligible_adult_count = where(
            has_adult_anchor,
            non_dependent_adult_count,
            unanchored_adult_count,
        )
        eligible_child_count = where(
            has_adult_anchor,
            anchored_child_count,
            unanchored_child_count,
        )

        one_adult_no_children = (eligible_adult_count == 1) & (
            eligible_child_count == 0
        )
        two_plus_adults_no_children = (eligible_adult_count >= 2) & (
            eligible_child_count == 0
        )
        one_adult_with_children = (eligible_adult_count == 1) & (
            eligible_child_count > 0
        )
        two_plus_adults_with_children = (eligible_adult_count >= 2) & (
            eligible_child_count > 0
        )
        ny_child_only = (
            (state_code == "NY")
            & (eligible_adult_count == 0)
            & (eligible_child_count > 0)
        )

        return select(
            [
                ny_child_only,
                one_adult_no_children,
                two_plus_adults_no_children,
                one_adult_with_children,
                two_plus_adults_with_children,
            ],
            [
                FamilyTierCategory.CHILD_ONLY,
                FamilyTierCategory.ONE_ADULT,
                FamilyTierCategory.TWO_ADULTS,
                FamilyTierCategory.ONE_ADULT_AND_ONE_OR_MORE_CHILDREN,
                FamilyTierCategory.TWO_ADULTS_AND_ONE_OR_MORE_CHILDREN,
            ],
            default=FamilyTierCategory.INDIVIDUAL_AGE_RATED,
        )
