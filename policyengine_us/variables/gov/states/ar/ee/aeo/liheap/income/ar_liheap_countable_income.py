from policyengine_us.model_api import *


class ar_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Arkansas LIHEAP countable income"
    defined_for = StateCode.AR
    reference = (
        # State plan sections 1.8 (page 5) and 1.9 (pages 6-7).
        "https://liheapch.acf.gov/docs/2026/state-plans/AR_Plan_2026.pdf#page=5",
        # FY2025 state plan sections 1.8 and 1.9, pages 5-7.
        "https://liheapch.acf.gov/docs/2025/state-plans/AR_Plan_2025.pdf#page=5",
        # Draft manual section 4.7 (MCI rounding, page 42; Medicare deduction,
        # section 4.7.2, page 43) and Appendices E-F (pages 130-144).
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2025/manuals/AR_Manual%5Bdraft%5D_2025.pdf#page=42",
        # Application section III, page 2.
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/fillable_aeo-9495_liheap-long-application.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ar.ee.aeo.liheap.income
        person = spm_unit.members
        age = person("age", period)
        # Manual Appendix F (page 133) excludes a child's earnings only while
        # the child attends school at least half time; plan Section 1.9 (page 6)
        # and application Section III (page 2) exclude all earnings under 18.
        # No input covers half-time attendance below college: K-12 enrollment
        # counts through is_full_time_student, and preschool, vocational and
        # training-program attendance have no input. is_full_time_student
        # defaults to true at ages 5-17, so a minor's earnings are excluded
        # unless school status is set to false.
        attends_school = person("is_full_time_student", period) | person(
            "is_part_time_college_student", period
        )
        excluded_child = (age < p.student_exclusion.child_age_limit) & attends_school
        # Manual Appendix F (page 134), row "Earnings of a full-time college
        # student", excludes full-time college students up to age 23 who are
        # dependents of a household member; application Section III excludes
        # every full-time student. The row text says "Income received"; the
        # model follows the heading and excludes only earned sources, so the
        # student's unearned income still counts. Reading the text instead
        # would exclude all of the student's income. Tax-unit dependency
        # stands for the dependent listing. Manual page 41 also excludes an
        # 18-year-old high-school student's earnings unless the student works
        # full time or is emancipated; that rule is not modeled.
        excluded_college_student = (
            person("is_full_time_college_student", period)
            & (age <= p.student_exclusion.college_max_age)
            & person("is_tax_unit_dependent", period)
        )
        counted_worker = ~(excluded_child | excluded_college_student)
        # Existing net business income approximates gross receipts. Additional
        # business/work-expense deductions and new gross inputs are deferred.
        # Each source is floored at zero, so a loss in one source cannot
        # offset another.
        earned_income = 0
        for source in p.sources.earned:
            earned_income = earned_income + max_(person(source, period), 0)
        countable_earnings = spm_unit.sum(earned_income * counted_worker) * (
            1 - p.earned_disregard
        )
        unearned_income = 0
        for source in p.sources.unearned:
            unearned_income = unearned_income + max_(person(source, period), 0)
        # Manual Appendix F (page 137) counts only the interest "amount over
        # $200.00". The amount is monthly because unearned income is a month's
        # receipts (page 41; Appendix E, pages 129-130, converts other
        # frequencies to monthly). The manual does not say whose $200 it is;
        # applying it to each recipient is a chosen reading, and a household-
        # wide $200 would count more. Plan Section 1.9 (page 6) counts
        # interest with no threshold.
        annual_interest_disregard = p.interest_disregard * MONTHS_IN_YEAR
        countable_interest = max_(
            person("interest_income", period) - annual_interest_disregard, 0
        )
        # Plan section 1.9 counts Social Security "Excluding MediCare
        # deduction", and manual section 4.7.2 excludes the Part B premium
        # from Social Security and Railroad Retirement for members not
        # eligible for Medicaid. medicare_part_b_premium is zero when not
        # enrolled and excludes the share a Medicare Savings Program pays.
        # Other medical deductions are not modeled.
        ssa_and_railroad = max_(person("social_security", period), 0) + max_(
            person("railroad_benefits", period), 0
        )
        premium = person("medicare_part_b_premium", period)
        net_ssa_and_railroad = max_(ssa_and_railroad - premium, 0)
        # Manual Appendix E (page 130) counts TEA once monthly; plan section
        # 1.9 leaves TANF unchecked. The annual tanf aggregate includes ar_tea
        # and applies take-up, so a nonrecipient's entitlement is not counted.
        tea = spm_unit("tanf", period)
        # Annual inputs approximate the month before application. Otherwise
        # countable income from every member is included in full, even when
        # that member is excluded from ar_liheap_household_size.
        annual_income = (
            countable_earnings
            + spm_unit.sum(unearned_income + countable_interest + net_ssa_and_railroad)
            + tea
        )
        # Manual page 42: round monthly countable income to the nearest whole
        # dollar before the income limit and band tests.
        monthly_income = np.floor(annual_income / MONTHS_IN_YEAR + 0.5)
        return monthly_income * MONTHS_IN_YEAR
