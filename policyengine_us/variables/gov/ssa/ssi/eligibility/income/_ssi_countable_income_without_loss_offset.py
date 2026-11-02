from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


def ssi_countable_income_without_loss_offset(person, period, parameters, sources):
    """
    Monthly SSI countable income as if the net loss of `sources` were 0.

    SSI nets a business loss against wages (POMS SI 00820.210). Some state
    programs that otherwise budget SSI countable income bar that offset for
    some or all businesses. This restores the net loss of `sources` to the
    person's own earned income, reapplies the SSI exclusions, and adds the
    difference to ssi_countable_income for the month.

    The adjustment works person by person on own earned and unearned income,
    so couple computations, spousal deeming and the blind or disabled
    working student exclusion are approximate.
    """
    year = period.this_year
    countable_income = person("ssi_countable_income", period)
    if not sources:
        return countable_income
    restored_loss = max_(-add(person, year, sources), 0)
    earned = person("ssi_earned_income", year)
    # Same unearned pool as ssi_countable_income, so the $20 general
    # exclusion splits between earned and unearned income the same way.
    unearned = (
        person("ssi_unearned_income", year)
        + person("ssi_unearned_income_deemed_from_ineligible_parent", year)
        + person("ssi_in_kind_support_and_maintenance", year)
    )
    with_offset = _apply_ssi_exclusions(earned, unearned, parameters, year)
    without_offset = _apply_ssi_exclusions(
        earned + restored_loss, unearned, parameters, year
    )
    # ssi_countable_income is zero for a person who is not SSI eligible.
    is_eligible = person("is_ssi_eligible_individual", year) | person(
        "is_ssi_eligible_spouse", year
    )
    adjustment = where(is_eligible, without_offset - with_offset, 0)
    return countable_income + adjustment / MONTHS_IN_YEAR
