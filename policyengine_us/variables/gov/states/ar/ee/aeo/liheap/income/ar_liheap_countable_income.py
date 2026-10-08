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
        # Draft manual sections 4.7 and 4.7.2 and Appendices E-F.
        # PDF pages 41-43, 130-144
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2025/manuals/AR_Manual%5Bdraft%5D_2025.pdf#page=41",
        # Application section III.
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/fillable_aeo-9495_liheap-long-application.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ar.ee.aeo.liheap.income
        person = spm_unit.members
        age = person("age", period)
        # Current application Section III requests work income only from
        # members 18 and older who are not full-time students. It states no
        # adult-student age or dependency restriction. These operating rules
        # supersede the narrower exclusions in the unadopted FY2025 draft.
        # The accepted plans also exclude earnings of children under 18.
        counted_worker = (age >= p.student_exclusion.child_age_limit) & ~person(
            "is_full_time_student", period
        )
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
