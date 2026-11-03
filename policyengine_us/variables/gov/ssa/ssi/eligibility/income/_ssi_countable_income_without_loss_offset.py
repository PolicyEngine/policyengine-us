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
    so couple computations and spousal deeming are approximate. It restores
    only the person's own barred loss: an ineligible spouse's barred loss
    still reduces the spouse's earnings before they are deemed, and the
    person's own leftover loss can still reduce the spouse's deemed
    earnings. Either can lower countable income below what the state rule
    gives.
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
    # ssi_countable_income takes the blind or disabled working student
    # exclusion (20 CFR 416.1112(c)(3)) off earned income before the other
    # exclusions, so take it again from the restored earnings.
    p = parameters(year).gov.ssa.ssi.income.exclusions.blind_or_disabled_working_student
    is_student = (
        person("is_ssi_blind_or_disabled_working_student_exclusion_eligible", year) > 0
    )

    def after_student_exclusion(amount):
        monthly = max_(amount, 0) / MONTHS_IN_YEAR
        exclusion = min_(min_(p.amount, monthly) * MONTHS_IN_YEAR, p.cap)
        return max_(amount - where(is_student, exclusion, 0), 0)

    with_offset = _apply_ssi_exclusions(
        after_student_exclusion(earned), unearned, parameters, year
    )
    without_offset = _apply_ssi_exclusions(
        after_student_exclusion(earned + restored_loss), unearned, parameters, year
    )
    # Same gate as ssi_countable_income, which is zero for a person who is
    # not aged, blind or disabled.
    is_aged_blind_disabled = person("is_ssi_aged_blind_disabled", year)
    adjustment = where(is_aged_blind_disabled, without_offset - with_offset, 0)
    return countable_income + adjustment / MONTHS_IN_YEAR
