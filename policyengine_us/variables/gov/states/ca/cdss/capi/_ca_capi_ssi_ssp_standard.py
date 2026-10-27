from policyengine_us.model_api import *


def ca_capi_ssi_ssp_standard(person, period, parameters):
    """Return a person's monthly SSI/SSP individual and couple standards.

    CAPI payment standards equal the SSI/SSP standards (WIC 18941), and the
    living arrangement selects one standard (MPP 49-050.2; POMS SI 01415.058
    B). These follow ca_state_supplement_payment_standard, whose amounts
    include the federal benefit rate:
    - Title XIX medical facility: the facility standard alone (MPP 49-050.26).
    - Nonmedical out-of-home care: one standard for every category, half the
      couple out-of-home care standard per person (MPP 49-050.24).
    - Independent living: the higher of the blind amount and the aged or
      disabled amount (the disabled child amount for a dependent child, MPP
      49-050.25; blind children take the blind amount, MPP 49-050.253). Only
      the aged or disabled amount adds the food allowance for people who
      cannot prepare meals (WIC 12200(e)); a couple with one blind member
      adds the individual food allowance for the other member (POMS SI
      01415.058 B.1 code C). California pays the highest category a person or
      couple qualifies for.
    In an SSI couple computation the couple standard sums both members'
    shares; otherwise it treats the ineligible spouse as the person's
    category (POMS SI 01320.430 C.7).
    NOTE: the reduced-needs standards for people living in another person's
    household (POMS SI 01415.058 code D) are not modeled; they need their own
    state supplement amounts (issue 7892).
    """
    p = parameters(period).gov.states.ca.cdss.state_supplement.payment_standard
    fbr = parameters(period).gov.ssa.ssi.amount
    age = person("monthly_age", period)
    child = person("is_tax_unit_dependent", period.this_year) & (
        age < p.dependent.age_limit
    )
    blind = person("is_blind", period.this_year)
    aged_or_disabled = (age >= p.aged_or_disabled.age_threshold) | person(
        "is_ssi_disabled", period.this_year
    )
    no_cooking = ~person.household(
        "living_arrangements_allow_for_food_preparation", period.this_year
    )
    medical_facility = person("ca_in_medical_care_facility", period.this_year)
    out_of_home_care = person("in_out_of_home_care_facility", period.this_year)
    out_of_home_care_share = (
        p.aged_or_disabled.amount.married + p.allowance.out_of_home_care
    ) / 2

    community_individual = max_(
        blind * p.blind.single,
        aged_or_disabled
        * where(
            child,
            p.dependent.amount,
            p.aged_or_disabled.amount.single + no_cooking * p.allowance.food.single,
        ),
    )

    joint = person("ssi_couple_computation_applies", period)
    blind_count = where(joint, person.marital_unit.sum(blind), 2 * blind)
    aged_or_disabled_count = where(
        joint, person.marital_unit.sum(aged_or_disabled), 2 * aged_or_disabled
    )
    two_blind = (blind_count > 1) * p.blind.married.two_blind
    one_blind = (blind_count == 1) * (
        p.blind.married.one_blind + no_cooking * p.allowance.food.single
    )
    aged_or_disabled_couple = select(
        [aged_or_disabled_count > 1, aged_or_disabled_count == 1],
        [
            p.aged_or_disabled.amount.married + no_cooking * p.allowance.food.married,
            p.aged_or_disabled.amount.single + no_cooking * p.allowance.food.single,
        ],
        default=0,
    )
    community_couple = max_(max_(two_blind, one_blind), aged_or_disabled_couple)

    # The state supplement amounts hold 1991 totals until 2025 (issue 7787),
    # below the federal benefit rate from 2008. CAPI equals SSI/SSP (WIC
    # 18941), and SSI alone pays at least the federal rate, so the
    # independent-living and out-of-home care standards are floored at it.
    individual = select(
        [medical_facility, out_of_home_care],
        [
            p.allowance.medical_care_facility,
            max_(out_of_home_care_share, fbr.individual),
        ],
        default=max_(community_individual, fbr.individual),
    )
    couple_share = select(
        [medical_facility, out_of_home_care],
        [
            p.allowance.medical_care_facility,
            max_(out_of_home_care_share, fbr.couple / 2),
        ],
        default=max_(community_couple / 2, fbr.couple / 2),
    )
    couple = where(joint, person.marital_unit.sum(couple_share), 2 * couple_share)
    return individual, couple
