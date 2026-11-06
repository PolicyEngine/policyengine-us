from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._apply_medicaid_optional_senior_or_disabled_exclusions import (
    _apply_medicaid_optional_senior_or_disabled_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.household.demographic.person._parent_links import (
    is_parent_of_any,
)


class medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent(
    Variable
):
    value_type = float
    entity = Person
    label = "Medicaid optional senior or disabled unearned income deemed from ineligible parent"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1165",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-020-00/0805-020-15/",
    )

    def formula(person, period, parameters):
        eligible_child = person("is_ssi_aged_blind_disabled", period) & person(
            "is_child", period
        )
        state = person.household("state_code_str", period)
        missouri = state == "MO"
        # Missouri deems a natural or adoptive parent's income: "Do not deem the
        # income of any other persons in the home, including a stepparent" (DSS
        # Manual § 0805.020.15). A stepparent's own child does not make them a
        # parent of the disabled child.
        ineligible_parent = person("is_ssi_ineligible_parent", period) & (
            ~missouri | is_parent_of_any(person, period, eligible_child)
        )
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

        child_allocations = eligible_child * add(
            tax_unit, period, ["ssi_ineligible_child_allocation"]
        )
        # Missouri's allowance is "the SSI maximum for the number of parents in
        # the home whose income was used in deeming" (DSS Manual § 0805.020.15
        # step 8), so a stepparent or a parent on SSI does not raise it.
        ssi = parameters(period).gov.ssa.ssi.amount
        deeming_parents = tax_unit.sum(ineligible_parent)
        missouri_allowance = (
            where(deeming_parents == 2, ssi.couple, deeming_parents * ssi.individual)
            * MONTHS_IN_YEAR
        )
        parental_allocations = eligible_child * where(
            missouri,
            missouri_allowance,
            add(tax_unit, period, ["ssi_ineligible_parent_allocation"]),
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
            ),
            _apply_medicaid_optional_senior_or_disabled_exclusions(
                parental_earned_income,
                parental_unearned_income,
                state,
                general_disregard,
                parameters,
                period,
            ),
        )
        net_parental_deemed_income = max_(
            0, net_parental_deemed_income - parental_allocations
        )

        count_eligible_children = tax_unit.sum(eligible_child)
        income = np.zeros_like(count_eligible_children, dtype=float)
        mask = count_eligible_children > 0
        income[mask] = net_parental_deemed_income[mask] / count_eligible_children[mask]
        return income
