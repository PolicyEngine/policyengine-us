from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
    _ssi_spouse_index,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


def ca_capi_in_title_xix_facility(person, period):
    """Whether a person lives in a Title XIX medical facility (MPP 49-050.26).

    Reads both the California input and SSI's living arrangement.
    """
    arrangement = person("ssi_federal_living_arrangement", period)
    return person("ca_in_medical_care_facility", period.this_year) | (
        arrangement == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
    )


def ca_capi_couple_computation(person, period):
    """Whether CAPI computes the person with their spouse as a couple.

    SSI's couple computation, except that a couple with exactly one spouse in
    a Title XIX facility is computed separately (20 CFR 416.414(b)(3)), when
    only the California facility input marks it.
    """
    in_facility = ca_capi_in_title_xix_facility(person, period)
    one_in_facility = (
        _ssi_couple_total(person, period.this_year, in_facility.astype(int)) == 1
    )
    return person("ssi_couple_computation_applies", period) & ~one_in_facility


def ca_capi_spouse_ssi_ssp(person, period):
    """Return the SSI and state supplement paid to the person's spouse.

    Only a spouse who is not CAPI-eligible counts. ca_state_supplement is an
    SPM-unit amount, so as a simplification the spouse's share is pro rata
    among the unit's members eligible for it; a citizen disabled child's
    supplement in the unit is then attributed to the spouse.
    """
    spouse_index = _ssi_spouse_index(person, period.this_year)
    safe_spouse = np.maximum(spouse_index, 0)
    spouse = (spouse_index >= 0) & ~person("ca_capi_eligible_person", period.this_year)[
        safe_spouse
    ]
    spouse_ssi = person("ssi", period)[safe_spouse] * spouse
    ssp_eligible = person("ca_state_supplement_eligible_person", period)
    spouse_ssp_share = (
        ssp_eligible[safe_spouse] * spouse / max_(person.spm_unit.sum(ssp_eligible), 1)
    )
    spouse_ssp = spouse_ssp_share * person.spm_unit("ca_state_supplement", period)
    return spouse_ssi + spouse_ssp


def ca_capi_ssi_ssp_standard(person, period, parameters):
    """Return a person's monthly SSI/SSP individual and couple standards.

    CAPI equals SSI/SSP (WIC 18941), and the living arrangement selects one
    standard (MPP 49-050.2; POMS SI 01415.058 B):
    - Title XIX medical facility: the facility standard alone (MPP 49-050.26).
    - Non-medical out-of-home care: one standard for every category, half the
      couple amount per person (WIC 12200(g); MPP 49-050.24).
    - Independent living: the highest category the person or couple qualifies
      for; the no-cooking allowance goes only with the aged or disabled amount
      (WIC 12200(e)), not the one-blind couple rate (12200(b)).
    Outside an SSI couple computation the ineligible spouse takes the person's
    category (POMS SI 01320.430 C.7).
    NOTE: reduced-needs standards (POMS SI 01415.058 code D) are not modeled
    (issue 7892).
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
    medical_facility = ca_capi_in_title_xix_facility(person, period)
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

    joint = ca_capi_couple_computation(person, period)
    blind_count = where(
        joint, _ssi_couple_total(person, period.this_year, blind.astype(int)), 2 * blind
    )
    aged_or_disabled_count = where(
        joint,
        _ssi_couple_total(person, period.this_year, aged_or_disabled.astype(int)),
        2 * aged_or_disabled,
    )
    two_blind = (blind_count > 1) * p.blind.married.two_blind
    one_blind = (blind_count == 1) * p.blind.married.one_blind
    # NOTE: a couple with one aged or disabled member always has a blind
    # member, whose rate is higher, so the second branch is only a guard.
    aged_or_disabled_couple = select(
        [aged_or_disabled_count > 1, aged_or_disabled_count == 1],
        [
            p.aged_or_disabled.amount.married + no_cooking * p.allowance.food.married,
            p.aged_or_disabled.amount.single + no_cooking * p.allowance.food.single,
        ],
        default=0,
    )
    community_couple = max_(max_(two_blind, one_blind), aged_or_disabled_couple)

    # Stopgap: the state supplement amounts hold 1991 totals until 2025,
    # below the federal benefit rate from 2008, so the independent-living and
    # out-of-home care standards are floored at that rate (SSI alone pays at
    # least it, and CAPI equals SSI/SSP under WIC 18941). This still leaves
    # out the whole state supplement before 2025; issue 10480 backfills the
    # totals and removes the floor.
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
    couple = where(
        joint,
        _ssi_couple_total(person, period.this_year, couple_share),
        2 * couple_share,
    )
    return individual, couple
