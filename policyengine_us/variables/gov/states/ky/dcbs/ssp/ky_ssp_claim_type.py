from policyengine_us.model_api import *


class KYSSPClaimType(Enum):
    INDIVIDUAL = "Individual"
    COUPLE_BOTH_ELIGIBLE = "Couple, both eligible"
    COUPLE_ONE_ELIGIBLE = "Couple, one eligible with ineligible spouse"


class ky_ssp_claim_type(Variable):
    value_type = Enum
    entity = Person
    label = "Kentucky SSP claim type"
    definition_period = MONTH
    defined_for = StateCode.KY
    possible_values = KYSSPClaimType
    default_value = KYSSPClaimType.INDIVIDUAL
    reference = (
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/015/",
        "https://www.chfs.ky.gov/agencies/dcbs/dfs/Documents/OMVOLV.pdf#page=41",
    )

    def formula(person, period, parameters):
        # §9(1)(c) couple rates apply to an "eligible couple" — both spouses
        # must qualify for SSP itself, not merely for SSI. The §4(1) SSP
        # categorical tests (SSI-eligible + age ≥ 18 + qualifying living
        # arrangement) are applied here. The §4(1)(b) income test is
        # intentionally excluded to avoid a cycle through
        # ky_ssp_payment_standard → ky_ssp_claim_type.
        is_ssi_eligible = person("is_ssi_eligible", period)
        is_adult = person("is_adult", period)
        category = person("ky_ssp_category", period)
        in_qualifying_category = category != category.possible_values.NONE
        ssp_categorically_eligible = is_ssi_eligible & is_adult & in_qualifying_category
        eligible_count = person.marital_unit.sum(ssp_categorically_eligible)
        marital_unit_size = person.marital_unit.nb_persons()
        both_eligible = (eligible_count == 2) & ssp_categorically_eligible
        one_eligible_couple = (
            (eligible_count == 1)
            & ssp_categorically_eligible
            & (marital_unit_size == 2)
        )
        return select(
            [both_eligible, one_eligible_couple],
            [
                KYSSPClaimType.COUPLE_BOTH_ELIGIBLE,
                KYSSPClaimType.COUPLE_ONE_ELIGIBLE,
            ],
            default=KYSSPClaimType.INDIVIDUAL,
        )
