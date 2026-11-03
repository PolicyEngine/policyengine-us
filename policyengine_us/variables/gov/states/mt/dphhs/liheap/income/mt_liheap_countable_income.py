from policyengine_us.model_api import *


class mt_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Montana LIHEAP annual countable income"
    defined_for = StateCode.MT
    reference = (
        "https://rules.mt.gov/policy-library-documents/application/pdf/325b36e5abb6a3bfa036c3802fc997ed50711b5407868ec8f4b61eabc538e3ed#page=1",
        "https://rules.mt.gov/policy-library-documents/application/pdf/fa158b2cdbf766e585e1fbf5811523e0dff4e760111590ae75d0456ee81551ad#page=1",
        # PDF pages 1-3
        "https://rules.mt.gov/policy-library-documents/application/pdf/36b451e63d1ed5ab982f4c43f746503d7b5d88dc720f10b0fc9b151576d6e788#page=1",
        # PDF pages 1-3
        "https://rules.mt.gov/policy-library-documents/application/pdf/67c0cce58f641eb9e573034d17d76e21e7c3c27f2f915180538f865766863b61#page=1",
        # PDF pages 30, 35-47
        "https://web.archive.org/web/20261015032646/https://dphhs.mt.gov/assets/hcsd/liheap/LIHEAPmanual.pdf#page=30",
        # PDF pages 6-7
        "https://liheapch.acf.gov/docs/2026/state-plans/MT_Plan_2026.pdf#page=6",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.liheap.income
        person = spm_unit.members
        # Every member's nonexcluded income counts (ARM 37.70.401(1)),
        # including that of minors and of ineligible noncitizen members (ARM
        # 37.70.402(8), numbered (7) from May 23, 2026).
        # Each source is floored at zero so a loss in one source cannot
        # offset another. Net business inputs stand in for receipts minus
        # self-employment deductions; the depreciation add-back, the optional
        # 60% of gross receipts calculation and the prior-year tax-return
        # method are not modeled.
        income = 0
        for source in p.sources.earned + p.sources.unearned:
            income = income + max_(person(source, period, options=[ADD]), 0)
        # ARM 37.70.407(1)(d): the dependents and survivors benefits that
        # continue for full-time students aged 18 to 22 are excluded.
        age = person("age", period)
        student = (
            (age >= p.student_minimum_age)
            & (age < p.student_age_limit)
            & person("is_full_time_student", period)
        )
        student_benefits = add(
            person, period, ["social_security_dependents", "social_security_survivors"]
        )
        social_security = max_(
            person("social_security", period) - where(student, student_benefits, 0),
            0,
        )
        # Medicare Part A and Part B premiums paid out of Social Security are
        # not income (manual section 3.15, Income Exclusions).
        medicare_premiums = add(
            person, period, ["medicare_part_a_premium", "medicare_part_b_premium"]
        )
        withheld_premiums = min_(medicare_premiums, social_security)
        # ARM 37.70.407(1)(w): a member's gifts count in full once they reach
        # the monthly minimum; from May 23, 2026 the rule excludes monetary
        # gifts and the minimum is infinite.
        gifts = max_(person("financial_assistance", period), 0)
        counted_gifts = where(gifts / MONTHS_IN_YEAR >= p.gift_minimum, gifts, 0)
        member_income = income + social_security - withheld_premiums + counted_gifts
        # Annual inputs stand in for one month of income annualized (ARM
        # 37.70.401(1); from May 23, 2026 calculated through CHIMES, with 12
        # months of self-employment receipts). No inputs hold Indian per
        # capita, lease or trust income above the $2,000 exclusions, plasma
        # sales or contract-for-deed payments, so those receipts are not
        # counted.
        tanf = max_(spm_unit("tanf", period), 0)
        # ARM 37.70.407(1)(bb): out-of-pocket health insurance premiums,
        # including Medicare premiums not paid out of Social Security, reduce
        # income, but not for categorically eligible households (manual
        # section 3.15).
        premiums = medicare_premiums - withheld_premiums
        for deduction in p.deductions:
            premiums = premiums + person(deduction, period)
        categorical = spm_unit("mt_liheap_categorical_eligibility", period)
        deductions = where(
            categorical == categorical.possible_values.NONE,
            spm_unit.sum(premiums),
            0,
        )
        return max_(spm_unit.sum(member_income) + tanf - deductions, 0)
