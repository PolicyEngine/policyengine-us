from policyengine_us.model_api import *


class AKSSPClaimType(Enum):
    INDIVIDUAL = "Individual"
    COUPLE_BOTH_ELIGIBLE = "Couple, both eligible"
    COUPLE_ONE_ELIGIBLE = "Couple, one eligible with ineligible spouse"


class ak_ssp_claim_type(Variable):
    value_type = Enum
    entity = Person
    label = "Alaska Adult Public Assistance claim type"
    definition_period = YEAR
    defined_for = StateCode.AK
    possible_values = AKSSPClaimType
    default_value = AKSSPClaimType.INDIVIDUAL
    reference = (
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ak.pdf#page=2"
    )

    def formula(person, period, parameters):
        joint_claim = person("ssi_claim_is_joint", period)
        marital_unit_size = person.marital_unit.sum(person("age", period) >= 0)
        living_arrangement = person("ak_ssp_living_arrangement", period)
        living_arrangement_values = living_arrangement.possible_values
        # Both spouses must share the same living arrangement to be
        # treated as a joint couple claim. New enum values added to
        # AKSSPLivingArrangement must be appended to this check.
        shared_living_arrangement = (
            (
                person.marital_unit.sum(
                    living_arrangement == living_arrangement_values.INDEPENDENT
                )
                == marital_unit_size
            )
            | (
                person.marital_unit.sum(
                    living_arrangement == living_arrangement_values.HOUSEHOLD_OF_ANOTHER
                )
                == marital_unit_size
            )
            | (
                person.marital_unit.sum(
                    living_arrangement == living_arrangement_values.ASSISTED_LIVING
                )
                == marital_unit_size
            )
            | (
                person.marital_unit.sum(
                    living_arrangement == living_arrangement_values.MEDICAID_FACILITY
                )
                == marital_unit_size
            )
        )
        is_eligible_individual = person("is_ssi_aged_blind_disabled", period)
        # COUPLE_ONE_ELIGIBLE requires exactly one spouse to be
        # individually ABD-eligible. If both spouses qualify but they
        # are not jointly claiming, they should not be misclassified
        # as a one-eligible couple.
        spouse_is_eligible = (
            person.marital_unit.sum(is_eligible_individual.astype(int))
            - is_eligible_individual.astype(int)
        ) > 0
        one_eligible_couple = (
            ~joint_claim
            & is_eligible_individual
            & ~spouse_is_eligible
            & (marital_unit_size == 2)
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
