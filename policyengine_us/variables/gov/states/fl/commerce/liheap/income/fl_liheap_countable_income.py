from policyengine_us.model_api import *


class fl_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Florida LIHEAP annual countable household income"
    defined_for = StateCode.FL
    # Plan section 1.9
    reference = (
        # PDF pages 5-7
        "https://liheapch.acf.gov/docs/2026/state-plans/FL_Plan_2026.pdf#page=5",
        # PDF pages 49-51
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/FL_PolicyManual_2023.pdf#page=49",
        # PDF pages 5-7
        "https://liheapch.acf.gov/docs/2025/state-plans/FL_Plan_2025.pdf#page=5",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.commerce.liheap.income
        person = spm_unit.members
        age = person("age", period)
        # Plan vs manual conflict; this follows the manual for earned and
        # unearned income alike. Manual 1200.01D (PDF p. 49): "Any income of a
        # household member 18 and older will be counted ... Income for any
        # persons ages 16 and 17 who do not attend school full time will be
        # counted." The FY2025 and FY2026 plans, item 1.9 (p. 6), leave
        # "Earned income of a child under the age of 18" unchecked, which
        # would exclude a 16- or 17-year-old nonstudent's earnings.
        income_counted = (age >= p.adult_age) | (
            (age >= p.nonstudent_min_age) & ~person("is_full_time_student", period)
        )
        # Use existing net business inputs without another expense deduction.
        # Plan section 1.8 counts gross income and manual 1200.01B counts "the
        # gross amount of income", so each source is floored at zero and a
        # loss in one source cannot offset another.
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        unearned = 0
        for source in p.sources.unearned:
            unearned = unearned + max_(person(source, period, options=[ADD]), 0)
        # Plan section 1.9 counts "net gambling or lottery winnings", so
        # losses offset only winnings.
        gambling = max_(
            person("gambling_winnings", period) - person("gambling_losses", period),
            0,
        )
        # Count TANF once at SPM level. The take-up-gated tanf total includes
        # fl_tca; fl_tca alone is the entitlement a nonrecipient could get.
        cash_grant = add(spm_unit, period, p.sources.household, options=[ADD])
        # Annual inputs approximate the prior 30 days/current economic situation.
        # Nonqualified members' countable income is retained in full. UI and
        # cash gifts are excluded by the plans. Gross SSA is included; the
        # manual expressly adds Medicare premiums back to net checks.
        # Existing inputs do not isolate work-study, royalties, mortgage/sale
        # installments, and all countable insurance/lump-sum receipts.
        return (
            spm_unit.sum((earned + unearned + gambling) * income_counted) + cash_grant
        )
