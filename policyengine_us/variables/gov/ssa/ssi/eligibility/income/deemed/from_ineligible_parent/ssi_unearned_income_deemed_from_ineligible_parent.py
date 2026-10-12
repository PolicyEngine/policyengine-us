from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.deemed.from_ineligible_parent._ssi_parental_deeming import (
    ssi_ineligible_parents,
    ssi_parental_deeming_children,
    ssi_parental_income,
)


class ssi_unearned_income_deemed_from_ineligible_parent(Variable):
    value_type = float
    entity = Person
    label = "SSI unearned income (deemed from ineligible parent)"
    documentation = (
        "The income of this child's ineligible parents that SSI deems to "
        "them, after the allocations for ineligible children and parents and "
        "the general and earned income exclusions, divided equally among the "
        "eligible children who share those parents."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1165",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320500",
    )

    def formula(person, period, parameters):
        rows, ineligible, pool = ssi_ineligible_parents(person, period)
        applies = person("is_ssi_income_deeming_child", period)
        # 416.1165(a): the ineligible parents' income.
        earned = ssi_parental_income(
            person, period, "ssi_earned_income", rows, ineligible
        )
        unearned = ssi_parental_income(
            person, period, "ssi_unearned_income", rows, ineligible
        )
        # 416.1165(b) and 416.1163(b)(3): allocations for ineligible children
        # come out of unearned income first, then earned income (416.1165(h),
        # Example 4).
        child_allocations = person("ssi_parental_deeming_child_allocations", period)
        remaining_child_allocations = max_(0, child_allocations - unearned)
        unearned = max_(0, unearned - child_allocations)
        earned = max_(0, earned - remaining_child_allocations)
        # 416.1165(d)(1)-(3): the $20 and earned income exclusions, then the
        # living allowance for the parents.
        net = max_(
            0,
            _apply_ssi_exclusions(earned, unearned, parameters, period)
            - person("ssi_parental_deeming_parent_allocation", period),
        )
        # 416.1165(e)(2): divide equally among the eligible children who share
        # these parents.
        children = ssi_parental_deeming_children(pool, applies)
        return where(applies, net / max_(1, children), 0)
