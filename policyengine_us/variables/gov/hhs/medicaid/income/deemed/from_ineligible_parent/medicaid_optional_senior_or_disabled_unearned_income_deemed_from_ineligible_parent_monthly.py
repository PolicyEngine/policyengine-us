from policyengine_us.variables.gov.ssa.ssi.eligibility.income._annual_input import (
    annual_input,
)
from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._apply_medicaid_optional_senior_or_disabled_exclusions import (
    _apply_medicaid_optional_senior_or_disabled_exclusions,
)
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
from policyengine_us.variables.household.demographic.person._parent_links import (
    is_parent_of_any,
)


class medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent_monthly(
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
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title42/html/USCODE-2024-title42-chap7-subchapXIX-sec1396a.htm",
        "https://www.ecfr.gov/current/title-42/section-435.601#p-435.601(d)(2)",
        "https://www.dmas.virginia.gov/media/mghpujpo/m05-1-1-26.pdf#page=57",
    )

    def formula(person, period, parameters):
        supplied = annual_input(
            person,
            period,
            "medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent",
        )
        if supplied is not None:
            return supplied / MONTHS_IN_YEAR

        # Medicaid's own immigration rules include eligible groups who do
        # not qualify for SSI, including state-covered noncitizen children.
        eligible_child = (
            person("is_ssi_aged_blind_disabled", period)
            & person("is_child", period)
            & person("is_medicaid_immigration_status_eligible", period)
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
        # A deeming spouse who files in another tax unit joins the pool, as in
        # SSI's parental deeming.
        spouse, spouse_files_elsewhere = _spouse_filing_elsewhere(
            person, period, ineligible_parent
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

        # Non-209(b) states retain SSI's allocation scope under
        # 42 USC 1396a(r)(2) and 42 CFR 435.601(d)(2)-(3).
        age = person("age", period.this_year)
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income.deeming
        allocation_child = (age < p.ineligible_child_age_limit[state]) & (
            ~p.ineligible_child_requires_nonblind_nondisabled[state].astype(bool)
            | ~person("is_ssi_aged_blind_disabled", period)
        )
        allocations = (
            person("ssi_ineligible_child_allocation_monthly", period) * allocation_child
        )
        # The allocation total already reaches the children of a parent's
        # spouse who files in another tax unit.
        child_allocations = eligible_child * ssi_parental_child_allocation_total(
            person, period, eligible_child, allocations
        )
        # Missouri's allowance is "the SSI maximum for the number of parents in
        # the home whose income was used in deeming" (DSS Manual § 0805.020.15
        # step 8), so a stepparent or a parent on SSI does not raise it.
        ssi = parameters(period).gov.ssa.ssi.amount
        # Count as integers: adding two boolean arrays would be a logical OR.
        deeming_parents = tax_unit.sum(
            ineligible_parent.astype(int) + spouse_files_elsewhere.astype(int)
        )
        missouri_allowance = where(
            deeming_parents == 2, ssi.couple, deeming_parents * ssi.individual
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
            missouri,
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

        count_eligible_children = _with_spouse_unit(
            person, spouse, spouse_files_elsewhere, tax_unit.sum(eligible_child)
        )
        income = np.zeros_like(count_eligible_children, dtype=float)
        mask = count_eligible_children > 0
        income[mask] = net_parental_deemed_income[mask] / count_eligible_children[mask]
        return where(eligible_child, income, 0)
