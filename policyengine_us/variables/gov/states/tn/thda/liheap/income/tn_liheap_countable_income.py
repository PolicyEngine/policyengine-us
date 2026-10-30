from policyengine_us.model_api import *


class tn_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Tennessee LIHEAP countable income"
    defined_for = StateCode.TN
    reference = (
        # PDF pages 8-9, 27-30
        "https://dogvxws799i6n.cloudfront.net/wp-content/uploads/LIHEAP-2026-Policy-Manual-for-Tennessee.pdf#page=8",
        # PDF pages 5-7
        "https://liheapch.acf.gov/docs/2026/state-plans/TN_Plan_2026.pdf#page=5",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tn.thda.liheap.income
        person = spm_unit.members
        # Annual inputs stand in for the income received in the 30 days before
        # application. Earned income counts for members 18 and over who are
        # not tax-unit dependents; unearned income counts for every member.
        earned_counted = (person("age", period) >= p.earned_income_min_age) & ~person(
            "is_tax_unit_dependent", period
        )
        # Income is gross cash receipts unless a source is listed as net, so
        # each source is floored at zero and a loss in one source cannot
        # offset another.
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        unearned = 0
        for source in p.sources.unearned:
            unearned = unearned + max_(person(source, period, options=[ADD]), 0)
        # Section 2.13 counts net income from Social Security, pensions
        # (including military retirement pay) and VA benefits excluding
        # Medicare premiums, and FY2026 plan Section 1.9 counts benefits
        # excluding the Medicare deduction. Each member's Part A and Part B
        # premiums are subtracted from those benefits, floored at zero.
        benefits = max_(person("social_security", period), 0)
        for source in p.sources.net_of_medicare:
            benefits = benefits + max_(person(source, period), 0)
        medicare_premiums = add(
            person, period, ["medicare_part_a_premium", "medicare_part_b_premium"]
        )
        net_benefits = max_(benefits - medicare_premiums, 0)
        # Interest counts only above the annual threshold and when withdrawn;
        # withdrawal has no input and is assumed. Section 2.13 names no unit
        # for the threshold; the model applies it to each member's interest.
        interest = max_(person("interest_income", period), 0)
        counted_interest = where(interest > p.interest_threshold, interest, 0)
        gambling = max_(
            person("gambling_winnings", period) - person("gambling_losses", period),
            0,
        )
        # Members excluded from household size keep all their income. TANF
        # (Families First) is counted once at the SPM level through the
        # take-up-gated tanf total.
        person_income = (
            earned * earned_counted
            + unearned
            + net_benefits
            + counted_interest
            + gambling
        )
        return spm_unit.sum(person_income) + spm_unit("tanf", period)
