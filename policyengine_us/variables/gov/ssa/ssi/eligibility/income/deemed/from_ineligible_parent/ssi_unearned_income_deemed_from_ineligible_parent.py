from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class ssi_unearned_income_deemed_from_ineligible_parent(Variable):
    value_type = float
    entity = Person
    label = "SSI unearned income (deemed from ineligible parent)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1165"

    def formula(person, period, parameters):
        eligible_child = person("is_ssi_aged_blind_disabled", period) & person(
            "is_child", period
        )
        ineligible_parent = person("is_ssi_ineligible_parent", period)
        tax_unit = person.tax_unit
        # 20 CFR 416.1160(d): a parent's spouse who lives with the child is an
        # ineligible parent too. When that spouse files in another tax unit,
        # their income still joins the parent's (416.1165), as the couple rate
        # in ssi_ineligible_parent_allocation already assumes.
        spouse = _ssi_spouse_index(person, period)
        tax_unit_id = tax_unit.reference_entity.members_entity_id
        spouse_files_elsewhere = (
            ineligible_parent
            & (spouse >= 0)
            & ineligible_parent[spouse]
            & (tax_unit_id[spouse] != tax_unit_id)
        )
        earned = person("ssi_earned_income", period)
        unearned = person("ssi_unearned_income", period)

        prereduction_parental_earned_income = eligible_child * tax_unit.sum(
            earned * ineligible_parent
            + where(spouse_files_elsewhere, earned[spouse], 0)
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

        child_allocations = eligible_child * add(
            tax_unit, period, ["ssi_ineligible_child_allocation"]
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
        )

        net_parental_deemed_income = max_(
            0, net_parental_deemed_income - parental_allocations
        )

        count_eligible_children = tax_unit.sum(eligible_child)
        # avoid array divide-by-zero warnings by not using where() function
        # see the following GitHub issue for more details:
        # https://github.com/PolicyEngine/policyengine-us/issues/2494
        income = np.zeros_like(count_eligible_children)
        mask = count_eligible_children > 0
        income[mask] = net_parental_deemed_income[mask] / count_eligible_children[mask]
        return income
