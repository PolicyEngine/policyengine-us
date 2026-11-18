from policyengine_us.variables.gov.ssa.ssi.eligibility.income._annual_input import (
    annual_input,
)
from policyengine_us.model_api import *


class ssi_ineligible_child_allocation_monthly(Variable):
    value_type = float
    entity = Person
    label = "SSI ineligible child allocation"
    unit = USD
    documentation = (
        "The allocation SSI deducts for this child from an ineligible "
        "spouse's or parent's income before deeming it. Which claimants it "
        "applies to is decided where the allocations are summed."
    )
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1163#p-416.1163(b)",
        "https://www.ecfr.gov/current/title-20/section-416.1161#p-416.1161(c)",
        "https://www.ecfr.gov/current/title-20/section-416.1165#p-416.1165(b)",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320185",
    )

    def formula(person, period, parameters):
        supplied = annual_input(person, period, "ssi_ineligible_child_allocation")
        if supplied is not None:
            return supplied / MONTHS_IN_YEAR

        p = parameters(period).gov.ssa.ssi
        # 416.1163(b): 'We do not allocate for ineligible children who are
        # receiving public income-maintenance payments.'
        allocated = person("is_ssi_ineligible_child", period) & ~person(
            "ssi_receives_public_income_maintenance", period
        )
        # 416.1163(b)(1): the couple rate less the individual rate, a month.
        monthly_allocation = p.amount.couple - p.amount.individual
        # 416.1163(b)(2) reduces it by the child's income as described in
        # 416.1161(c), which excludes a student's earned income up to the
        # amounts in 416.1112(c)(3), whether or not the child is blind or
        # disabled (POMS SI 01320.185). No $20 or $65 exclusion applies.
        student = p.income.exclusions.blind_or_disabled_working_student
        is_student = person("is_full_time_student", period) & (
            person("age", period.this_year) < student.age_limit
        )
        # Annual income is spread evenly over the year. Keep each month's
        # allocation through downstream deductions, exclusions and benefit
        # caps; annual reads sum the completed monthly budgets.
        earned = max_(0, person("ssi_earned_income", period))
        unearned = max_(0, person("ssi_unearned_income", period))
        # The student exclusion is used consecutively from January until
        # its annual cap is exhausted (POMS SI 00820.510). Annual income
        # inputs imply the same monthly earnings in the preceding months.
        monthly_exclusion = min_(student.amount, earned)
        used = monthly_exclusion * (period.start.month - 1)
        exclusion_left = max_(0, student.cap - used)
        exclusion = where(is_student, min_(monthly_exclusion, exclusion_left), 0)
        income = earned - exclusion + unearned
        return allocated * max_(0, monthly_allocation - income)
