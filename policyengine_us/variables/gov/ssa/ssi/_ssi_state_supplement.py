from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


def ssi_state_supplement(
    person, period, parameters, individual_rate, couple_rate, federal_payment_rules=True
):
    """Apply SSI-based supplement income, couple and spouse-deeming rules.

    Rates are state supplements, excluding federal SSI. Each member supplies
    the same-category couple rate; averaging these rates implements mixed
    arrangements where the state's published schedule supports that method.
    Set federal_payment_rules only for SSA-administered payments; state
    administrators do not inherit the federal rounding or minimum payment.
    Sources: 20 CFR 416.2025; POMS SI 01320.430 D, SI 02005.030 G,
    SI 02001.005 and SI 02001.010. Callers apply state-specific eligibility.
    """
    joint = person("ssi_couple_computation_applies", period)
    couple_total = person.marital_unit.sum(couple_rate / 2)
    standard = where(joint, couple_total / 2, individual_rate)
    countable = person("ssi_countable_income", period)
    federal_amount = person("ssi_amount_if_eligible", period)
    excess = max_(countable - federal_amount, 0)
    payment = max_(standard - excess, 0)

    deeming = person("is_ssi_spousal_deeming_applies", period)
    deemed = person("ssi_income_deemed_from_ineligible_spouse", period)
    own_income = max_(countable - deemed, 0)
    ssi = parameters(period).gov.ssa.ssi
    federal_la = person("ssi_federal_living_arrangement", period)
    own_federal_amount = ssi.amount.individual * where(
        federal_la == SSIFederalLivingArrangement.ANOTHER_PERSONS_HOUSEHOLD,
        1 - ssi.amount.one_third_reduction_rate,
        1,
    )
    own_payment = max_(individual_rate - max_(own_income - own_federal_amount, 0), 0)
    # SI 01320.430 D.2: use the higher individual rate where it exceeds
    # the couple rate (including New Jersey's ineligible-spouse variation).
    deemed_payment = max_(max_(couple_rate, individual_rate) - excess, 0)
    payment = where(deeming, min_(own_payment, deemed_payment), payment)

    eligible = person("is_ssi_eligible", period) & person(
        "takes_up_ssi_if_eligible", period.this_year
    )
    # Federal administration discards digits beyond the third decimal place,
    # rounds up to cents, and pays at least one dollar for a positive amount.
    rounded = np.ceil(np.floor(payment * 1_000) / 10) / 100
    federal_payment = where(
        rounded > 0, max_(rounded, ssi.state_supplement.minimum_payment), 0
    )
    return eligible * where(federal_payment_rules, federal_payment, payment)
