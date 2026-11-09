from policyengine_us.model_api import *


class la_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Louisiana LIHEAP countable income"
    defined_for = StateCode.LA
    reference = (
        # PDF pages 29-30, 82-85
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20REVISED%20January%201_%202024.pdf#page=29",
        # PDF pages 34-36, 89-92
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20FINAL%20-%20Effective%20April%201%2c%202026.pdf#page=34",
        # PDF pages 5-7
        "https://liheapch.acf.gov/docs/2026/state-plans/LA_Plan_2026.pdf#page=5",
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20Frequently%20Asked%20Questions%20(FAQs)%20-%202%2011%2022.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.la.lhc.liheap.income
        person = spm_unit.members
        # Annual inputs approximate the monthly income of the 30 days before
        # application. The guide counts "Any income of a household member age
        # 18 and older"; earned income also excludes members still enrolled in
        # high school.
        adult = person("age", period) >= p.adult_age
        earned_counted = adult & ~person("is_in_k12_school", period)
        # The guide counts gross income unless a source is listed as net, so
        # each source is floored at zero and a loss in one source cannot offset
        # another.
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        unearned = 0
        for source in p.sources.unearned:
            unearned = unearned + max_(person(source, period), 0)
        # Appendix E (Lump Sum rows) counts net gambling and lottery winnings and
        # excludes other non-recurring lump sums. FY2026 plan Section 1.9 checks
        # one-time lump-sum payments generally; the guide is followed.
        gambling = max_(
            person("gambling_winnings", period) - person("gambling_losses", period),
            0,
        )
        # Appendix E (Social Security Benefits row) counts Social Security
        # benefits, including SSI, "paid to minors", and FAQ A4 counts the
        # Social Security a parent receives for a minor child, so both count
        # for every member. Other benefits paid for minors are not counted. The
        # guide counts "Net Social Security Administration (SSA) benefits" and
        # FY2026 plan Section 1.9 counts them excluding the Medicare deduction,
        # so the Part B premium the person pays is subtracted.
        social_security = max_(
            person("social_security", period)
            - person("medicare_part_b_premium", period),
            0,
        )
        ssi = person("ssi", period, options=[ADD])
        # Undocumented members keep all their income. FITAP is counted once at
        # the SPM level: the take-up-gated tanf total includes la_fitap, which
        # alone would count a grant a nonrecipient could get.
        person_income = (
            earned * earned_counted
            + (unearned + gambling) * adult
            + social_security
            + ssi
        )
        return spm_unit.sum(person_income) + spm_unit("tanf", period)
