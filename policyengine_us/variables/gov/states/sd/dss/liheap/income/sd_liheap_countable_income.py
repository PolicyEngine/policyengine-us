from policyengine_us.model_api import *


class sd_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "South Dakota LIEAP annual countable household income"
    defined_for = StateCode.SD
    reference = (
        "https://sdlegislature.gov/Rules/Administrative/67:15:01:18",
        "https://sdlegislature.gov/Rules/Administrative/67:15:01:18.01",
        "https://liheapch.acf.gov/docs/2026/state-plans/SD_Plan_2026.pdf#page=6",
        # PDF pages 17, 25-28
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/SD_Policy-and-Procedures-Manual2018.pdf#page=17",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sd.dss.liheap.income
        person = spm_unit.members
        age = person("age", period)
        excluded_earnings = (age < p.earned_income_min_age) | (
            (age < p.secondary_school_age_limit)
            & person("is_in_secondary_school", period)
        )
        # Rule 67:15:01:18.01 counts self-employment losses as zero, and the
        # manual (page 25) computes rental income on the self-employment sheet.
        # Each source is floored at zero, so a loss in one source cannot offset
        # another. Use existing net sources without another business deduction.
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        unearned = 0
        for source in p.sources.unearned:
            # ADD sums monthly sources such as ssi over the year.
            unearned = unearned + max_(person(source, period, options=[ADD]), 0)
        # Rule 67:15:01:18(12) excludes "Deductions from social security benefit
        # payments for Medicare", and the manual (page 28) counts Social Security
        # less the Part B and Part D premiums. medicare_part_b_premium is zero for
        # a person who is not enrolled and excludes the share a Medicare Savings
        # Program pays; no Part D premium input exists.
        premium = person("medicare_part_b_premium", period)
        social_security = max_(person("social_security", period) - premium, 0)
        # Rule 67:15:01:18(1) exempts earnings, not minor unearned income.
        income = spm_unit.sum(earned * ~excluded_earnings + unearned + social_security)
        # The annual tanf aggregate includes sd_tanf and applies take-up; sd_tanf
        # alone is the entitlement a nonrecipient could get.
        tanf = spm_unit("tanf", period)
        # Subsection (20) excludes income used to pay child support.
        child_support_paid = add(spm_unit, period, ["child_support_expense"])
        # Manual physical page 17: for ineligible members, "a portion of their
        # income and resources are considered when determining the household
        # benefit" through the Citizenship Income Calculator (also page 26). The
        # calculator's proration formula is not published and is unclear: its one
        # example turns $3,000 eligible and $4,000 ineligible income into $6,200,
        # matching neither full counting ($7,000) nor SNAP pro rata ($6,000). The
        # model counts ineligible members' income in full, which overstates
        # income for mixed-status households.
        # Annual inputs approximate stable income over the prior three months.
        # Existing inputs cannot isolate all jury/foster receipts, program
        # overpayment withholding, or expense refunds.
        return max_(income + tanf - child_support_paid, 0)
