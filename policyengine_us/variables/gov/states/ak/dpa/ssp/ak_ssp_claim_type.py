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
        is_eligible_individual = person("is_ssi_aged_blind_disabled", period)
        one_eligible_couple = (
            ~joint_claim & is_eligible_individual & (marital_unit_size == 2)
        )
        return select(
            [joint_claim, one_eligible_couple],
            [
                AKSSPClaimType.COUPLE_BOTH_ELIGIBLE,
                AKSSPClaimType.COUPLE_ONE_ELIGIBLE,
            ],
            default=AKSSPClaimType.INDIVIDUAL,
        )
