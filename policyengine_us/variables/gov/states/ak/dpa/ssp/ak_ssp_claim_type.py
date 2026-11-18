from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class AKSSPClaimType(Enum):
    INDIVIDUAL = "Individual"
    COUPLE_BOTH_ELIGIBLE = "Couple, both eligible"
    COUPLE_ONE_ELIGIBLE = "Couple, one eligible with ineligible spouse"


class ak_ssp_claim_type(Variable):
    value_type = Enum
    entity = Person
    label = "Alaska Adult Public Assistance claim type"
    definition_period = MONTH
    defined_for = StateCode.AK
    possible_values = AKSSPClaimType
    default_value = AKSSPClaimType.INDIVIDUAL
    reference = (
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ak.pdf#page=2"
    )

    def formula(person, period, parameters):
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        # The spouse is the co-resident husband or wife the SSI joint claim
        # uses, so a third adult in a default marital unit is not counted.
        spouse = _ssi_spouse_index(person, period.this_year)
        has_spouse = spouse >= 0
        partner = np.where(has_spouse, spouse, np.arange(person.count))
        # Both spouses must share the same living arrangement to be
        # treated as a joint couple claim.
        living_arrangement = person("ak_ssp_living_arrangement", period)
        shared_living_arrangement = living_arrangement == living_arrangement[partner]
        is_eligible_individual = person("is_ssi_aged_blind_disabled", period.this_year)
        # COUPLE_ONE_ELIGIBLE requires exactly one spouse to be
        # individually ABD-eligible. If both spouses qualify but they
        # are not jointly claiming, they should not be misclassified
        # as a one-eligible couple.
        spouse_is_eligible = has_spouse & is_eligible_individual[partner]
        one_eligible_couple = (
            ~joint_claim & is_eligible_individual & has_spouse & ~spouse_is_eligible
        )
        couple_both_eligible = joint_claim & shared_living_arrangement
        return select(
            [couple_both_eligible, one_eligible_couple],
            [
                AKSSPClaimType.COUPLE_BOTH_ELIGIBLE,
                AKSSPClaimType.COUPLE_ONE_ELIGIBLE,
            ],
            default=AKSSPClaimType.INDIVIDUAL,
        )
