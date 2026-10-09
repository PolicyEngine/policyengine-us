from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.irs_gross_income.social_security.dependent_taxable_ss_magi import (
    dependent_income_and_deductions,
)
from policyengine_us.variables.household.expense.retirement._ira_supplied_contributions import (
    traditional_ira_contributions_without_spousal_rule,
)


class dependent_traditional_ira_deduction(Variable):
    value_type = float
    entity = Person
    label = "Dependent's traditional IRA deduction on their own return"
    unit = USD
    documentation = (
        "The IRC 219 deduction a tax unit dependent takes on their own return "
        "for their own traditional IRA contributions. It is limited to the "
        "dependent's compensation and the dollar limit. An active participant "
        "in an employer plan is phased out on the single schedule (the "
        "separate schedule if they live with their spouse), using their own "
        "modified AGI. That modified AGI leaves out taxable Social Security, "
        "which IRC 219(g)(3)(A)(i) would add; this only matters for an active "
        "participant with income near the phase-out range. The filer's "
        "traditional_ira_deduction excludes dependents, whose contributions "
        "are not on the filer's return."
    )
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#b_1",
        "https://www.law.cornell.edu/uscode/text/26/219#g",
        "https://www.irs.gov/publications/p590a",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.ald.ira.phase_out
        retirement = parameters(period).gov.irs.gross_income.retirement_contributions
        catch_up = person("age", period) >= retirement.catch_up.age_threshold
        dollar_limit = retirement.limit.ira + catch_up * retirement.catch_up.limit.ira
        compensation = person("ira_compensation", period)
        # The spousal rule never reaches a dependent, so their contributions
        # are figured on their own limit. This avoids the filer's filing
        # status, which itself depends on who is a dependent.
        contributions = traditional_ira_contributions_without_spousal_rule(
            person, period, min_(dollar_limit, compensation)
        )
        active = person("ira_active_participant", period)
        lives_with_spouse = person("dependent_lives_with_spouse", period)
        start = where(lives_with_spouse, p.start.SEPARATE, p.start.SINGLE)
        width = where(lives_with_spouse, p.width.SEPARATE, p.width.SINGLE)
        # IRC 219(g)(3)(A)(ii): modified AGI is figured without this deduction.
        income, deductions = dependent_income_and_deductions(person, period, parameters)
        other_deductions = [
            d for d in deductions if d != "dependent_traditional_ira_deduction"
        ]
        magi = (income - add(person, period, other_deductions)).astype(np.float64)
        fraction = clip((magi - start) / width, 0, 1)
        # Section 219(g)(2)(C) rounds the reduction down to a multiple of $10.
        reduction = (
            np.floor(np.round(dollar_limit * fraction, 6) / p.rounding_interval)
            * p.rounding_interval
        )
        phased_limit = where(
            magi >= start + width,
            0,
            max_(p.minimum, dollar_limit - reduction),
        )
        limit = min_(compensation, where(active, phased_limit, dollar_limit))
        return min_(contributions, limit)
