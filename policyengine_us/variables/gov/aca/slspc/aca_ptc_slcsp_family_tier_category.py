from policyengine_us.model_api import *
from policyengine_us.variables.gov.aca.slspc.slcsp_family_tier_category import (
    FamilyTierCategory,
    family_tier_category,
)


class aca_ptc_slcsp_family_tier_category(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = FamilyTierCategory
    default_value = FamilyTierCategory.INDIVIDUAL_AGE_RATED
    definition_period = MONTH
    label = "ACA family tier category for the premium tax credit coverage family"
    defined_for = "slcsp_family_tier_applies"
    reference = "https://www.law.cornell.edu/cfr/text/26/1.36B-3#f"
    documentation = (
        "The family tier (New York and Vermont) of the coverage family's "
        "benchmark plan: slcsp_family_tier_category counted over coverage "
        "family members only, so an enrollee who can be claimed on another "
        "return does not move the tier."
    )

    def formula(tax_unit, period, parameters):
        covered = tax_unit.members("is_aca_coverage_family_member", period.this_year)
        return family_tier_category(tax_unit, period, parameters, covered)
