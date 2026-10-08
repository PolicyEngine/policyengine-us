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
        "https://storage.googleapis.com/florida-liheap-relief-static-assets/Florida_LIHEAP_Application_English.pdf#page=1",
        "https://floridaliheap.com/faq",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.commerce.liheap.income
        person = spm_unit.members
        age = person("age", period)
        # The current statewide application excludes all minors' income,
        # matching the portal FAQ. The FY2026 plan endorses this portal in
        # section 1.10. This supersedes the older manual's nonstudent exception.
        # The application was created in March 2025 but supplies no rule-change
        # effective date; applying it throughout FY2025 is a backfilled assumption.
        income_counted = age >= p.adult_age
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
