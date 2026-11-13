from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
)


def _rate(parameter, period):
    # These rates are read for every person, and each state's start after the
    # earliest years the model computes (California's in 1991), where the
    # parameter tree has no value; read them as zero there.
    value = parameter(period.start)
    return 0 if value is None else value


def _ssi_parent_supplement_rates(person, period, parameters):
    """Monthly at-home state supplement rates for an individual and a couple.

    20 CFR 416.1166 counts a federally administered State supplement as an SSI
    benefit, and POMS SI 01320.630 B.1 deems from parents only the income
    "in excess of what is required to reduce the parents' FBR and any
    Federally-administered State supplement to zero". A parent whose income is
    deemed lives at home with the child. Of the 12 states in POMS SI 01415.058
    A, only California (B), New Jersey (J) and Vermont (M) pay such a parent a
    federally administered supplement in every category. Delaware, the District
    of Columbia, Hawaii, Michigan, Montana and Rhode Island pay one only in care
    or facility settings, and Pennsylvania only in care homes or with an
    essential person, so their rates here are zero.
    NOTE: Nevada pays aged or blind people at home (I), and Iowa pays blind
    people and people living with a dependent (F); the model has no rates for
    either, so their parents are tested against the federal rate alone. Before
    New Jersey's (2026) and Vermont's (2017) parameters start, their parents are
    tested against the federal rate alone too.
    The rates read parameters, not the state supplement variables, because those
    depend on is_ssi_ineligible_parent. The facility and care-home rates do not
    apply to a parent living with the child.
    """
    state = person.household("state_code_str", period)
    joint = person("ssi_claim_is_joint", period)
    blind = person("is_blind", period)

    # California, WIC 12200 and POMS SI 01415.058 B: the highest category the
    # person or couple qualifies for. Outside a joint claim the ineligible
    # spouse takes the person's category (POMS SI 01320.430 C.7), as in
    # ca_state_supplement_rates.
    ca = parameters.gov.states.ca.cdss.state_supplement.payment_standard
    age_threshold = _rate(ca.aged_or_disabled.age_threshold, period)
    aged_or_disabled_single = _rate(ca.aged_or_disabled.amount.single, period)
    aged_or_disabled_married = _rate(ca.aged_or_disabled.amount.married, period)
    food_single = _rate(ca.allowance.food.single, period)
    food_married = _rate(ca.allowance.food.married, period)
    blind_single = _rate(ca.blind.single, period)
    one_blind = _rate(ca.blind.married.one_blind, period)
    two_blind = _rate(ca.blind.married.two_blind, period)
    aged_or_disabled = (person("age", period) >= age_threshold) | (
        person("is_ssi_disabled", period)
    )
    no_cooking = ~person.household(
        "living_arrangements_allow_for_food_preparation", period
    )
    ca_individual = max_(
        blind * blind_single,
        aged_or_disabled * (aged_or_disabled_single + no_cooking * food_single),
    )
    blind_count = where(
        joint, _ssi_couple_total(person, period, blind.astype(int)), 2 * blind
    )
    aged_or_disabled_count = where(
        joint,
        _ssi_couple_total(person, period, aged_or_disabled.astype(int)),
        2 * aged_or_disabled,
    )
    ca_couple = max_(
        max_((blind_count > 1) * two_blind, (blind_count == 1) * one_blind),
        (aged_or_disabled_count > 1)
        * (aged_or_disabled_married + no_cooking * food_married),
    )

    # New Jersey, POMS SI 01415.058 J: a parent with a child in the home is in
    # code B, "Living alone or with others"; code C covers a recipient who lives
    # "with ONLY their ineligible spouse".
    nj = parameters.gov.states.nj.njdhs.ssp.amount
    nj_individual = _rate(nj.individual.LIVING_ALONE_OR_WITH_OTHERS, period)
    nj_couple = _rate(nj.couple.LIVING_ALONE_OR_WITH_OTHERS, period)

    # Vermont, POMS SI 01415.058 M: independent living covers a recipient "not
    # living in the household of another".
    vt = parameters.gov.states.vt.dcf.aabd.amount
    vt_individual = _rate(vt.individual.INDEPENDENT, period)
    vt_couple = _rate(vt.couple.INDEPENDENT, period)

    individual = select(
        [state == "CA", state == "NJ", state == "VT"],
        [ca_individual, nj_individual, vt_individual],
        default=0,
    )
    couple = select(
        [state == "CA", state == "NJ", state == "VT"],
        [ca_couple, nj_couple, vt_couple],
        default=0,
    )
    return individual, couple


def _ssi_parent_supplement_level(person, period, parameters):
    """Annual state supplement that an aged, blind or disabled parent is tested on.

    It follows the supplement standard in ssi_state_supplement: the couple rate
    for a joint claim, the higher of the couple and individual rates when an
    ineligible spouse's income is deemed (POMS SI 01320.430 D.2), and the
    individual rate otherwise. It is zero for a parent who is not aged, blind
    or disabled, and outside the states in _ssi_parent_supplement_rates.
    """
    individual, couple = _ssi_parent_supplement_rates(person, period, parameters)
    joint = person("ssi_claim_is_joint", period)
    deeming = person("is_ssi_spousal_deeming_applies", period)
    monthly = select(
        [joint, deeming],
        [couple, max_(couple, individual)],
        default=individual,
    )
    return person("is_ssi_aged_blind_disabled", period) * monthly * MONTHS_IN_YEAR
