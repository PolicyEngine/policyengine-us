from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


def ca_in_title_xix_facility(person, period):
    """Whether a person lives in a Title XIX medical facility (MPP 49-050.26).

    Reads both the California input and SSI's living arrangement.
    """
    arrangement = person("ssi_federal_living_arrangement", period)
    return person("ca_in_medical_care_facility", period.this_year) | (
        arrangement == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
    )


def ca_state_supplement_rates(person, period, parameters, joint):
    """Return a person's monthly state shares at the individual and couple rates.

    WIC 12200 sets one standard for each recipient or married couple, and the
    living arrangement selects it (MPP 49-050.2; POMS SI 01415.058 B):
    - Title XIX medical facility: the facility share alone (WIC 12200(h)).
    - Non-medical out-of-home care: one share for every category, including
      children (WIC 12200(g)).
    - Independent living: the highest category the person or couple qualifies
      for (POMS SI 01415.058 B.2 note). A blind child takes the blind share
      (WIC 12200(a)), and a disabled child under 18 the disabled minor share
      (WIC 12200(f)). The no-cooking allowance goes only with the aged or
      disabled share (WIC 12200(e)), not the blind or disabled minor shares.
    The couple rate is for the whole couple, and only a head or spouse has one.
    Outside a joint computation the ineligible spouse takes the person's
    category (POMS SI 01320.430 C.7).
    NOTE: the household-of-another shares (POMS SI 01415.058 codes D, F and G)
    are not modeled (issue 7892), so those recipients keep these shares.
    NOTE: a child in a non-parent relative's home takes the out-of-home care
    share (POMS SI 01415.058 B.1 code B) only with in_out_of_home_care_facility.
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
    # NOTE: living_arrangements_allow_for_food_preparation defaults to true
    # and the microdata do not set it, so the no-cooking allowance (+$128.87
    # a month in 2026, +$257.74 for a couple) applies only when the input is
    # set to false (issue 10296).
    no_cooking = ~person.household(
        "living_arrangements_allow_for_food_preparation", period.this_year
    )
    medical_facility = ca_in_title_xix_facility(person, period)
    out_of_home_care = person("in_out_of_home_care_facility", period.this_year)

    community_individual = max_(
        blind * p.blind.single,
        aged_or_disabled
        * where(
            child,
            p.dependent.amount,
            p.aged_or_disabled.amount.single + no_cooking * p.allowance.food.single,
        ),
    )
    individual = select(
        [medical_facility, out_of_home_care],
        [p.allowance.medical_care_facility, p.allowance.out_of_home_care],
        default=community_individual,
    )

    head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
    blind_count = where(
        joint, person.marital_unit.sum(blind & head_or_spouse), 2 * blind
    )
    aged_or_disabled_count = where(
        joint,
        person.marital_unit.sum(aged_or_disabled & head_or_spouse),
        2 * aged_or_disabled,
    )
    two_blind = (blind_count > 1) * p.blind.married.two_blind
    one_blind = (blind_count == 1) * p.blind.married.one_blind
    # NOTE: a couple with one aged or disabled member always has a blind
    # member, whose rate is higher, so only two count here. That couple gets no
    # allowance. POMS code C adds the individual allowance for it; PolicyEngine
    # follows the statute (ruled 2026-10-29, PR 10379 comment 6509402355).
    aged_or_disabled_couple = (aged_or_disabled_count > 1) * (
        p.aged_or_disabled.amount.married + no_cooking * p.allowance.food.married
    )
    community_couple = max_(max_(two_blind, one_blind), aged_or_disabled_couple)
    # The couple out-of-home care total is twice the individual total, so its
    # share moves with the federal rates (CDSS 2026 May Revision, page 26).
    out_of_home_care_couple = (
        2 * (fbr.individual + p.allowance.out_of_home_care) - fbr.couple
    )
    couple = select(
        [medical_facility, out_of_home_care],
        [p.allowance.medical_care_facility_couple, out_of_home_care_couple],
        default=community_couple,
    )
    return individual, couple * head_or_spouse
