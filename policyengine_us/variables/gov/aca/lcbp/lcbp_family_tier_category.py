from policyengine_us.model_api import *
from policyengine_us.variables.gov.aca.slspc.slcsp_family_tier_category import (
    FamilyTierCategory,
)


class lcbp_family_tier_category(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = FamilyTierCategory
    default_value = FamilyTierCategory.INDIVIDUAL_AGE_RATED
    definition_period = MONTH
    label = "ACA bronze family tier category for premium calculation"
    defined_for = "slcsp_family_tier_applies"

    def formula(tax_unit, period, parameters):
        state_code = tax_unit.household("state_code_str", period)
        max_child_age = parameters(period).gov.aca.slcsp.max_child_age

        person = tax_unit.members
        member_ages = person("monthly_age", period)
        pays_premium = person("pays_aca_premium", period)

        is_adult = member_ages > max_child_age
        eligible_adult_count = tax_unit.sum(is_adult & pays_premium)
        eligible_people = tax_unit.sum(pays_premium)
        eligible_child_count = eligible_people - eligible_adult_count

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
