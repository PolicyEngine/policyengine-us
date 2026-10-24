from policyengine_us.model_api import *


def ca_capi_ssi_ssp_standard(person, period, parameters):
    """Return a person's monthly SSI/SSP individual and couple standards.

    CAPI payment standards equal the SSI/SSP standards less an offset (MPP
    49-050.1). These follow ca_state_supplement_payment_standard, whose amounts
    include the federal benefit rate: the higher of the blind amount and the
    aged or disabled amount (the disabled child amount for a dependent child,
    MPP 49-050.25; blind children take the blind amount, MPP 49-050.253), the
    food allowance for an aged or disabled adult who cannot prepare meals, and
    the out-of-home-care and medical-care-facility allowances per person.
    In an SSI couple computation the couple standard uses both members;
    otherwise it treats the ineligible spouse as the person's category (POMS
    SI 01320.430 C.7) and adds only the person's own allowances.
    """
    p = parameters(period).gov.states.ca.cdss.state_supplement.payment_standard
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
    allowance = (
        person("in_out_of_home_care_facility", period.this_year)
        * p.allowance.out_of_home_care
        + person("ca_in_medical_care_facility", period.this_year)
        * p.allowance.medical_care_facility
    )
    individual = (
        max_(
            blind * p.blind.single,
            aged_or_disabled
            * where(child, p.dependent.amount, p.aged_or_disabled.amount.single),
        )
        + aged_or_disabled * ~child * no_cooking * p.allowance.food.single
        + allowance
    )

    joint = person("ssi_couple_computation_applies", period)
    blind_count = where(joint, person.marital_unit.sum(blind), 2 * blind)
    aged_or_disabled_count = where(
        joint, person.marital_unit.sum(aged_or_disabled), 2 * aged_or_disabled
    )
    blind_amount = select(
        [blind_count > 1, blind_count == 1],
        [p.blind.married.two_blind, p.blind.married.one_blind],
        default=0,
    )
    aged_or_disabled_amount = select(
        [aged_or_disabled_count > 1, aged_or_disabled_count == 1],
        [p.aged_or_disabled.amount.married, p.aged_or_disabled.amount.single],
        default=0,
    )
    food = (
        (aged_or_disabled_count > 0)
        * no_cooking
        * where(
            aged_or_disabled_count > 1,
            p.allowance.food.married,
            p.allowance.food.single,
        )
    )
    couple = (
        max_(blind_amount, aged_or_disabled_amount)
        + food
        + where(joint, person.marital_unit.sum(allowance), allowance)
    )
    return individual, couple
