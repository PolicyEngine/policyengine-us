from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_cdcc_single_parent_work_requirement() -> Reform:
    """
    Reform that changes CDCTC eligibility to require at least one parent to work
    instead of both parents.

    Current law: For married couples, childcare expenses are capped at the
    minimum of the two spouses' earnings, effectively requiring both to work.

    This reform: Changes the cap to the maximum of the two spouses' earnings,
    allowing families to qualify if at least one parent works.

    Note: We override cdcc_relevant_expenses directly (rather than
    min_head_spouse_earned) to avoid affecting state programs that also
    use min_head_spouse_earned.
    """

    class cdcc_relevant_expenses(Variable):
        value_type = float
        entity = TaxUnit
        label = "CDCC-relevant care expenses"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.law.cornell.edu/uscode/text/26/21#c",
            "https://www.law.cornell.edu/uscode/text/26/21#d_1",
        )

        def formula(tax_unit, period, parameters):
            expenses = tax_unit("tax_unit_childcare_expenses", period)
            cdcc_limit = tax_unit("cdcc_limit", period)
            eligible_capped_expenses = min_(expenses, cdcc_limit)

            # Reform: Use max of head/spouse earnings instead of min
            # This allows eligibility if at least one parent works
            is_joint = tax_unit("tax_unit_is_joint", period)
            head_earnings = tax_unit("head_earned", period)
            spouse_earnings = tax_unit("spouse_earned", period)
            earnings_cap = where(
                is_joint, max_(head_earnings, spouse_earnings), head_earnings
            )

            return min_(eligible_capped_expenses, earnings_cap)

    class reform(Reform):
        def apply(self):
            self.update_variable(cdcc_relevant_expenses)

    return reform


def create_cdcc_single_parent_work_requirement_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_cdcc_single_parent_work_requirement()

    p = parameters.gov.contrib.cdcc.single_parent_work_requirement

    # Check if reform is active in current period or next 5 years
    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_cdcc_single_parent_work_requirement()
    else:
        return None


cdcc_single_parent_work_requirement = (
    create_cdcc_single_parent_work_requirement_reform(None, None, bypass=True)
)
