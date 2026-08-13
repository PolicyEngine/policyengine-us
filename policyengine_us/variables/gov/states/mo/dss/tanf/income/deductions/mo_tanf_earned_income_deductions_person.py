from policyengine_us.model_api import *


class mo_tanf_earned_income_deductions_person(Variable):
    value_type = float
    entity = Person
    label = "Missouri TANF earned income deductions for one earner"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-30/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-30-10/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-30-20/",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        # 13 CSR 40-2.310(9)(A) and (9)(D) apply the disregards to each
        # participant's earned income separately; DSS Manual
        # 0210.015.30.10: "If more than one person has earned income,
        # apply the $30 plus 1/3 disregard to each person's net income."
        # Note: Missouri time-limits these disregards ($30 plus one-third
        # for four consecutive months, $30-only for the following eight
        # months, and the two-thirds disregard for up to 12 consecutive
        # months). These month counts are not modeled.
        # For a self-employment loss (negative gross), both branches
        # return the negative gross unchanged, so the loss cancels exactly
        # against the same person's gross in mo_tanf_countable_income.
        # Do not floor earnings here without flooring
        # mo_tanf_gross_earned_income in the same change — a one-sided
        # floor breaks the cancellation.
        p = parameters(period).gov.states.mo.dss.tanf.earned_income_disregard
        gross_earned = person("tanf_gross_earned_income", period)
        is_enrolled = person.spm_unit("is_tanf_enrolled", period)
        # Not an active TA participant when employment began (DSS Manual
        # 0210.015.30.10): deduct the standard work exemption first, then
        # $30, then one-third of the remainder.
        work_expense = min_(gross_earned, p.amount)
        after_work_expense = max_(gross_earned - p.amount, 0)
        thirty = min_(after_work_expense, p.thirty_plus_one_third.flat_amount)
        one_third = (after_work_expense - thirty) * p.thirty_plus_one_third.percentage
        new_applicant = work_expense + thirty + one_third
        # Active TA participant when employment began (DSS Manual
        # 0210.015.30.20; 13 CSR 40-2.310(9)(D)): apply the two-thirds
        # disregard to gross earnings first, then the work exemption.
        two_thirds = gross_earned * p.two_thirds_disregard.percentage
        enrolled_work_expense = min_(gross_earned - two_thirds, p.amount)
        enrolled = two_thirds + enrolled_work_expense
        return where(is_enrolled, enrolled, new_applicant)
