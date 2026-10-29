from policyengine_us.variables.gov.ssa.ssi.eligibility.income._annual_input import (
    annual_input,
)
from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.deemed.from_ineligible_parent._ssi_parental_child_allocation_scope import (
    ssi_parental_child_allocation_total,
)


class ssi_unearned_income_deemed_from_ineligible_parent_monthly(Variable):
    value_type = float
    entity = Person
    label = "SSI unearned income (deemed from ineligible parent)"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1165"

    def formula(person, period, parameters):
        supplied = annual_input(
            person, period, "ssi_unearned_income_deemed_from_ineligible_parent"
        )
        if supplied is not None:
            return supplied / MONTHS_IN_YEAR

        immigration_status = person("immigration_status", period)
        is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
        # 416.1165(e)(2) divides only among SSI-eligible children. Income
        # and resource eligibility depend on this calculation, so use the
        # status conditions shared with the ineligible-child classification.
        eligible_child = (
            person("is_ssi_aged_blind_disabled", period)
            & person("is_child", period)
            & (is_citizen | person("is_ssi_qualified_noncitizen", period))
        )
        ineligible_parent = person("is_ssi_ineligible_parent", period)
        tax_unit = person.tax_unit

        prereduction_parental_earned_income = eligible_child * tax_unit.sum(
            person("ssi_earned_income", period) * ineligible_parent
        )
        blind_disabled_working_student_income = person(
            "ssi_blind_or_disabled_working_student_exclusion", period
        )
        parental_earned_income = max_(
            prereduction_parental_earned_income - blind_disabled_working_student_income,
            0,
        )

        parental_unearned_income = eligible_child * tax_unit.sum(
            person("ssi_unearned_income", period) * ineligible_parent
        )

        child_allocations = eligible_child * ssi_parental_child_allocation_total(
            person, period, eligible_child
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

        count_eligible_children = tax_unit.sum(eligible_child)
        # avoid array divide-by-zero warnings by not using where() function
        # see the following GitHub issue for more details:
        # https://github.com/PolicyEngine/policyengine-us/issues/2494
        income = np.zeros_like(count_eligible_children, dtype=float)
        mask = count_eligible_children > 0
        income[mask] = net_parental_deemed_income[mask] / count_eligible_children[mask]
        return where(eligible_child, income, 0)
