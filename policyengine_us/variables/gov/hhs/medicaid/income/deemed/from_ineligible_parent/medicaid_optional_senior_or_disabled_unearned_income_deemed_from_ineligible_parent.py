from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._apply_medicaid_optional_senior_or_disabled_exclusions import (
    _apply_medicaid_optional_senior_or_disabled_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.deemed.from_ineligible_parent._ssi_parental_child_allocation_scope import (
    ssi_parental_child_allocation_total,
)


class medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent(
    Variable
):
    value_type = float
    entity = Person
    label = "Medicaid optional senior or disabled unearned income deemed from ineligible parent"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1165",
        "https://www.law.cornell.edu/uscode/text/42/1396b#v",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-020-00/0805-020-15/",
    )

    def formula(person, period, parameters):
        # Medicaid's own immigration rules include eligible groups who do
        # not qualify for SSI, including state-covered noncitizen children.
        eligible_child = (
            person("is_ssi_aged_blind_disabled", period)
            & person("is_child", period)
            & person("is_medicaid_immigration_status_eligible", period)
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

        state = person.household("state_code_str", period)
        # State allocation definitions can be narrower than SSI's adult
        # student definition. Apply each sourced ceiling before deducting
        # the shared allocation amount; other states retain their existing
        # shared allocation behavior.
        age = person("age", period.this_year)
        age_limits = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income.deeming.ineligible_child_age_limit
        allocation_child = np.ones(person.count, dtype=bool)
        for state_code in age_limits._children:
            allocation_child &= (state != state_code) | (age < age_limits[state_code])
        # These states define allocation children as nonblind and
        # nondisabled, independently of Medicaid immigration eligibility.
        allocation_child &= ~(
            np.isin(state, ("FL", "LA", "NY", "VA", "WI"))
            & person("is_ssi_aged_blind_disabled", period)
        )
        # Wisconsin includes dependent 18-year-olds, rather than all
        # adult students below 19. Dependency uses the existing tax-unit
        # role proxy, as elsewhere in the model.
        allocation_child &= (
            (state != "WI") | (age < 18) | person("is_tax_unit_dependent", period)
        )
        allocations = (
            person("ssi_ineligible_child_allocation", period) * allocation_child
        )
        child_allocations = eligible_child * ssi_parental_child_allocation_total(
            person, period, eligible_child, allocations
        )
        parental_allocations = eligible_child * add(
            tax_unit, period, ["ssi_ineligible_parent_allocation"]
        )

        parental_unearned_income -= child_allocations
        remaining_child_allocations = max_(0, -parental_unearned_income)
        parental_unearned_income = max_(0, parental_unearned_income)
        parental_earned_income = max_(
            0, parental_earned_income - remaining_child_allocations
        )

        general_disregard = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income.disregard.individual[
            state
        ]
        # Missouri deems parental income in the SSI order: the $20
        # exclusion comes off before the $65 and the half (DSS Manual
        # § 0805.020.15 steps 4-6), unlike its applicant budget.
        net_parental_deemed_income = where(
            state == "MO",
            _apply_ssi_exclusions(
                parental_earned_income,
                parental_unearned_income,
                parameters,
                period,
                general_exclusion=general_disregard,
                monthly=True,
            ),
            _apply_medicaid_optional_senior_or_disabled_exclusions(
                parental_earned_income * MONTHS_IN_YEAR,
                parental_unearned_income * MONTHS_IN_YEAR,
                state,
                general_disregard,
                parameters,
                period,
            )
            / MONTHS_IN_YEAR,
        )
        net_parental_deemed_income = max_(
            0, net_parental_deemed_income - parental_allocations
        )

        count_eligible_children = tax_unit.sum(eligible_child)
        income = np.zeros_like(count_eligible_children, dtype=float)
        mask = count_eligible_children > 0
        income[mask] = net_parental_deemed_income[mask] / count_eligible_children[mask]
        return where(eligible_child, income, 0)
