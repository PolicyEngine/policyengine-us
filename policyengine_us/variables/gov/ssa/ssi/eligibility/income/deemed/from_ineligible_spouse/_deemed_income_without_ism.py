"""Annual spousal deemed income for a reader that leaves out in-kind support."""

from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._annual_input import (
    annual_input,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


def ssi_income_deemed_from_ineligible_spouse_without_ism(person, period, parameters):
    """Return a year's income deemed from an ineligible spouse without the
    claimant's in-kind support and maintenance (ISM).

    is_ssi_ineligible_parent tests a parent's own income without ISM, since
    ISM depends on the living arrangement and the living arrangement depends
    on that test. This amount puts the spouse's deemed income on the same
    basis. ssi_income_deemed_from_ineligible_spouse adds the claimant's ISM to
    both budgets (POMS SI 01320.150 B.1.a), so reading it there would close
    that loop. A supplied annual ssi_income_deemed_from_ineligible_spouse, or
    its neutralization or abolition, still takes precedence.
    """
    supplied = annual_input(person, period, "ssi_income_deemed_from_ineligible_spouse")
    if supplied is not None:
        return supplied

    deeming_applies = person("is_ssi_spousal_deeming_applies", period)
    own_earned = person("ssi_earned_income", period)
    own_unearned = person("ssi_unearned_income", period)
    spouse_earned = person("ssi_earned_income_deemed_from_ineligible_spouse", period)
    spouse_unearned = person(
        "ssi_unearned_income_deemed_from_ineligible_spouse", period
    )
    # 20 CFR 416.1163(d)(2): combined countable income less the claimant's own.
    alone_countable = _apply_ssi_exclusions(
        own_earned, own_unearned, parameters, period
    )
    couple_countable = _apply_ssi_exclusions(
        own_earned + spouse_earned,
        own_unearned + spouse_unearned,
        parameters,
        period,
    )
    deemed = deeming_applies * max_(0, couple_countable - alone_countable)
    return where(person("is_ssi_aged_blind_disabled", period), deemed, 0)
