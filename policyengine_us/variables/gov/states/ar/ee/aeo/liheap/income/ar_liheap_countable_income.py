from policyengine_us.model_api import *


class ar_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Arkansas LIHEAP countable income"
    defined_for = StateCode.AR
    reference = (
        # FY2026 state plan sections 1.8 and 1.9.
        # PDF pages 5-7
        "https://liheapch.acf.gov/docs/2026/state-plans/AR_Plan_2026.pdf#page=5",
        # FY2025 state plan sections 1.8 and 1.9.
        # PDF pages 5-7
        "https://liheapch.acf.gov/docs/2025/state-plans/AR_Plan_2025.pdf#page=5",
        # FFY 2025 manual sections 4.7-4.7.4, the section 17.0 Full-time Student
        # definition and Appendices E-F.
        # PDF pages 56-59, 62-63, 141, 154-168
        "https://liheapch.acf.gov/docs/2025/manuals/AR_Manual_2025.pdf#page=56",
        # Application LIHEAP 9495 R 11/2025, Section III.
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/fillable_aeo-9495_liheap-long-application.pdf#page=2",
        # FY2025 application AEO 9495 R 01/FY2025, Section III (Wayback capture).
        "https://web.archive.org/web/20250104155015id_/https://www.adeq.state.ar.us/energy/assistance/pdfs/fillable_aeo-9495_liheap-long-application.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ar.ee.aeo.liheap.income
        person = spm_unit.members
        age = person("age", period)
        # Both application forms (AEO 9495 R 01/FY2025 and LIHEAP 9495 R
        # 11/2025, Section III) request work income only from members "18 and
        # older & not a full-time student" without defining the term, so the
        # manual's definition applies. The section 17.0 definition (page 141)
        # covers a full-time student "up to age 23" (read as inclusive) who is
        # a dependent of a household member: a college student enrolled for
        # twelve or more credit hours (also Appendix F, page 159) or a high
        # school student over 18. is_tax_unit_dependent stands for that
        # dependency; without supplied tax-unit roles or that input, age-ordered
        # inference can make a single parent's adult student the spouse (issue
        # 9868). Section 4.7 (page 56) excludes the earnings of members aged 18
        # in high school, dependent or not, "unless working full time or the
        # individual is emancipated and applying as the head of household";
        # those exceptions are not modeled. is_in_k12_school is imputed only
        # through age 17, so a high school student 18 or older is captured via
        # is_in_secondary_school. Appendix F (page 158) excludes a child's
        # earnings only during at least half-time school attendance; following
        # both forms, every member under 18 has earnings excluded.
        in_high_school = person("is_in_secondary_school", period) | person(
            "is_in_k12_school", period
        )
        full_time_student = (
            person("is_full_time_college_student", period) | in_high_school
        )
        dependent_student = (
            full_time_student
            & person("is_tax_unit_dependent", period)
            & (age <= p.full_time_student_age_limit)
        )
        high_school_student = in_high_school & (age <= p.high_school_student_age_limit)
        counted_worker = (
            (age >= p.earned_minimum_age) & ~dependent_student & ~high_school_student
        )
        # Business inputs are already net of expenses, which stands in for the
        # manual's 10% operating-cost allowance on gross self-employment income
        # (Appendix F, page 166); no further business or work-expense deduction
        # applies. Each source is floored at zero (section 4.7.4, page 63), so a
        # loss in one source cannot offset another.
        earned_income = 0
        for source in p.sources.earned:
            earned_income = earned_income + max_(person(source, period), 0)
        countable_earnings = spm_unit.sum(earned_income * counted_worker) * (
            1 - p.earned_disregard
        )
        unearned_income = 0
        for source in p.sources.unearned:
            unearned_income = unearned_income + max_(person(source, period), 0)
        # Manual Appendix F (page 162) counts only the interest "amount over
        # $200.00". The amount is monthly because unearned income is a month's
        # receipts (section 4.7, page 57; Appendix E, pages 154-155, converts
        # other frequencies to monthly). The manual does not say whose $200 it
        # is; applying it to each recipient is a chosen reading, and a
        # household-wide $200 would count more. Plan Section 1.9 (page 6)
        # counts interest with no threshold.
        annual_interest_disregard = p.interest_disregard * MONTHS_IN_YEAR
        countable_interest = max_(
            person("interest_income", period) - annual_interest_disregard, 0
        )
        # Plan section 1.9 counts Social Security "Excluding MediCare
        # deduction", and manual section 4.7.2 (page 59) excludes the Part B
        # premium from Social Security and Railroad Retirement for members not
        # eligible for Medicaid. medicare_part_b_premium is zero when not
        # enrolled and excludes the share a Medicare Savings Program pays.
        # Other medical deductions are not modeled.
        ssa_and_railroad = max_(person("social_security", period), 0) + max_(
            person("railroad_benefits", period), 0
        )
        premium = person("medicare_part_b_premium", period)
        net_ssa_and_railroad = max_(ssa_and_railroad - premium, 0)
        # Manual Appendix E (page 155) counts TEA once monthly; plan section
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
        # Manual page 58: round monthly countable income to the nearest whole
        # dollar before the income limit and band tests.
        monthly_income = np.floor(annual_income / MONTHS_IN_YEAR + 0.5)
        return monthly_income * MONTHS_IN_YEAR
