from policyengine_us.model_api import *


class ssi_ineligible_child_allocation(Variable):
    value_type = float
    entity = Person
    label = "SSI ineligible child allocation"
    unit = USD
    documentation = (
        "The allocation SSI deducts for this child from an ineligible "
        "spouse's or parent's income before deeming it. Which claimants it "
        "applies to is decided where the allocations are summed."
    )
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1163#p-416.1163(b)",
        "https://www.ecfr.gov/current/title-20/section-416.1161#p-416.1161(c)",
        "https://www.ecfr.gov/current/title-20/section-416.1165#p-416.1165(b)",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssi
        # 416.1163(b): 'We do not allocate for ineligible children who are
        # receiving public income-maintenance payments.'
        allocated = person("is_ssi_ineligible_child", period) & ~person(
            "ssi_receives_public_income_maintenance", period
        )
        # 416.1163(b)(1): the couple rate less the individual rate.
        allocation = (p.amount.couple - p.amount.individual) * MONTHS_IN_YEAR
        # 416.1163(b)(2) reduces it by the child's income as described in
        # 416.1161(c), which excludes a student's earned income up to the
        # amounts in 416.1112(c)(3).
        student = p.income.exclusions.blind_or_disabled_working_student
        earned = person("ssi_earned_income", period)
        is_student = person("is_full_time_student", period) & (
            person("age", period) < student.age_limit
        )
        monthly_exclusion = min_(student.amount, earned / MONTHS_IN_YEAR)
        student_exclusion = is_student * min_(
            monthly_exclusion * MONTHS_IN_YEAR, student.cap
        )
        income = earned - student_exclusion + person("ssi_unearned_income", period)
        return allocated * max_(0, allocation - income)
