from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._apply_medicaid_optional_senior_or_disabled_exclusions import (
    _apply_medicaid_optional_senior_or_disabled_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.deemed.from_ineligible_parent._ssi_parental_deeming import (
    ssi_ineligible_parents,
    ssi_parental_deeming_child,
    ssi_parental_deeming_child_allocation_total,
    ssi_parental_deeming_children,
    ssi_parental_deeming_parent_allocation_total,
    ssi_parental_income,
)


class medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent(
    Variable
):
    value_type = float
    entity = Person
    label = "Medicaid optional senior or disabled unearned income deemed from ineligible parent"
    documentation = (
        "Parental income deemed to a disabled child under the SSI rules of "
        "20 CFR 416.1165, with the state's income disregards. The parents "
        "and the ineligible children are those of SSI parental deeming, "
        "except that a disabled child need not meet the SSI citizenship or "
        "qualified-noncitizen condition (Medicaid applies its own immigration "
        "rules) and a disabled child who shares the deemed income takes no "
        "allocation. Missouri deems only a natural or adoptive parent's "
        "income, never a stepparent's, and allocates for every other child "
        "under 18 in the home who is not applying (DSS Manual 0805.020.15)."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1165",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-020-00/0805-020-15/",
    )

    def formula(person, period, parameters):
        state = person.household("state_code_str", period)
        missouri = state == "MO"
        # Missouri: 'Do not deem the income of any other persons in the home,
        # including a stepparent' (0805.020.15).
        rows, ineligible, pool = ssi_ineligible_parents(
            person, period, with_spouses=~missouri
        )
        # Medicaid applies its own immigration rules, so a disabled child
        # need not meet the SSI citizenship or qualified-noncitizen condition.
        applies = ssi_parental_deeming_child(
            person, period, ineligible, ssi_status=False
        )
        earned = ssi_parental_income(
            person, period, "ssi_earned_income", rows, ineligible
        )
        unearned = ssi_parental_income(
            person, period, "ssi_unearned_income", rows, ineligible
        )
        # Missouri allocates for 'each child under 18 living in the home who
        # is not applying for MA' (0805.020.15 step 1). A disabled child who
        # shares the deemed income takes no allocation.
        child_allocations = where(
            np.any(ineligible, axis=1),
            ssi_parental_deeming_child_allocation_total(
                person,
                period,
                rows,
                pool,
                applies,
                every_minor=missouri,
                exclude=applies,
            ),
            0,
        )
        remaining_child_allocations = max_(0, child_allocations - unearned)
        unearned = max_(0, unearned - child_allocations)
        earned = max_(0, earned - remaining_child_allocations)

        general_disregard = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income.disregard.individual[
            state
        ]
        # Missouri deems parental income in the SSI order: the $20
        # exclusion comes off before the $65 and the half (DSS Manual
        # § 0805.020.15 steps 4-6), unlike its applicant budget.
        net = where(
            missouri,
            _apply_ssi_exclusions(
                earned,
                unearned,
                parameters,
                period,
                general_exclusion=general_disregard,
            ),
            _apply_medicaid_optional_senior_or_disabled_exclusions(
                earned,
                unearned,
                state,
                general_disregard,
                parameters,
                period,
            ),
        )
        # Missouri: 'the SSI maximum for the number of parents in the home
        # whose income was used in deeming'.
        net = max_(
            0,
            net
            - ssi_parental_deeming_parent_allocation_total(
                parameters, period, np.sum(ineligible, axis=1)
            ),
        )
        children = ssi_parental_deeming_children(pool, applies)
        return where(applies, net / max_(1, children), 0)
