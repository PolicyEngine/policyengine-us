"""Monthly parental deeming, shared by SSI and state supplements."""

from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.deemed.from_ineligible_parent._parent_pool import (
    _spouse_filing_elsewhere,
    _with_spouse_unit,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.deemed.from_ineligible_parent._ssi_parental_child_allocation_scope import (
    ssi_parental_child_allocation_total,
)


def ssi_parental_deemed_income(
    person, period, parameters, allocations=None, recipients=None
):
    """Income deemed to each eligible child from ineligible parents in a month.

    20 CFR 416.1165. `allocations` gives each person's ineligible-child
    allocation; it defaults to SSI's. A state supplement whose own rules
    define an ineligible child more narrowly passes its own allocations, so
    its parental budget follows its rules while SSI's stays unchanged.
    `recipients` can replace the SSI recipient set for a state program.
    """
    if recipients is None:
        immigration_status = person("immigration_status", period)
        is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
        # 416.1165(e)(2) divides only among SSI-eligible children. Income
        # and resource eligibility depend on this calculation, so use the
        # status conditions shared with the ineligible-child classification.
        recipients = (
            person("is_ssi_aged_blind_disabled", period)
            & person("is_child", period)
            & (is_citizen | person("is_ssi_qualified_noncitizen", period))
        )
    eligible_child = recipients
    ineligible_parent = person("is_ssi_ineligible_parent", period)
    tax_unit = person.tax_unit
    # 416.1160(d): a parent's spouse who lives with the child is an ineligible
    # parent too, so a deeming spouse who files in another tax unit joins the
    # pool.
    spouse, spouse_files_elsewhere = _spouse_filing_elsewhere(
        person, period, ineligible_parent
    )
    earned = person("ssi_earned_income", period)
    unearned = person("ssi_unearned_income", period)

    prereduction_parental_earned_income = eligible_child * tax_unit.sum(
        earned * ineligible_parent + where(spouse_files_elsewhere, earned[spouse], 0)
    )
    blind_disabled_working_student_income = person(
        "ssi_blind_or_disabled_working_student_exclusion", period
    )
    parental_earned_income = max_(
        prereduction_parental_earned_income - blind_disabled_working_student_income,
        0,
    )

    parental_unearned_income = eligible_child * tax_unit.sum(
        unearned * ineligible_parent
        + where(spouse_files_elsewhere, unearned[spouse], 0)
    )

    # The allocation total already reaches the children of a parent's spouse
    # who files in another tax unit, so it takes no spouse-unit addition.
    child_allocations = eligible_child * ssi_parental_child_allocation_total(
        person, period, eligible_child, allocations
    )
    parental_allocations = eligible_child * add(
        tax_unit, period, ["ssi_ineligible_parent_allocation"]
    )

    # To understand this ordering of operations, see Example 4 of
    # https://www.law.cornell.edu/cfr/text/20/416.1165#h.

    parental_unearned_income -= child_allocations
    remaining_child_allocations = max_(0, -parental_unearned_income)
    parental_unearned_income = max_(0, parental_unearned_income)
    parental_earned_income = max_(
        0, parental_earned_income - remaining_child_allocations
    )

    net_parental_deemed_income = _apply_ssi_exclusions(
        parental_earned_income,
        parental_unearned_income,
        parameters,
        period,
        monthly=True,
    )

    net_parental_deemed_income = max_(
        0, net_parental_deemed_income - parental_allocations
    )

    # 416.1165(e)(2) divides the pooled income among both units' eligible
    # children.
    count_eligible_children = _with_spouse_unit(
        person, spouse, spouse_files_elsewhere, tax_unit.sum(eligible_child)
    )
    # avoid array divide-by-zero warnings by not using where() function
    # see the following GitHub issue for more details:
    # https://github.com/PolicyEngine/policyengine-us/issues/2494
    income = np.zeros_like(count_eligible_children, dtype=float)
    mask = count_eligible_children > 0
    income[mask] = net_parental_deemed_income[mask] / count_eligible_children[mask]
    return where(eligible_child, income, 0)
