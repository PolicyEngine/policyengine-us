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
        "https://secure.ssa.gov/poms.nsf/lnx/0501320185",
    )

    def formula(person, period, parameters):
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
            person("age", period) < student.age_limit
        )
        # Annual income is spread evenly over the year. The student
        # exclusion applies month by month until its yearly limit is used
        # up (POMS SI 00820.510), and each month's allocation is floored at
        # zero, so income left over in one month never reduces another's.
        monthly_earned = person("ssi_earned_income", period) / MONTHS_IN_YEAR
        monthly_unearned = person("ssi_unearned_income", period) / MONTHS_IN_YEAR
        exclusion_left = where(is_student, student.cap, 0)
        total = np.zeros(person.count)
        for _ in range(MONTHS_IN_YEAR):
            exclusion = min_(min_(student.amount, monthly_earned), exclusion_left)
            exclusion_left = exclusion_left - exclusion
            income = monthly_earned - exclusion + monthly_unearned
            total += max_(0, monthly_allocation - income)
        return allocated * total
