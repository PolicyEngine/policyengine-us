from policyengine_us.model_api import *


class wy_lieap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Wyoming LIEAP countable income"
    documentation = (
        "Annual income approximates current monthly income. All members' otherwise "
        "countable income is retained, including members excluded from household "
        "size by immigration status. Under approved assumptions, all under-18 "
        "earnings, TANF, child support received and identifiable lump sums are "
        "excluded. Total veterans benefits proxy service-connected disability "
        "payments and receive one household-size poverty exclusion per SPM unit. "
        "This proxy can understate income from other kinds of VA benefits. "
        "Annual source inputs cannot distinguish embedded lump sums, exempt "
        "reimbursements or irregular receipts; supply countable income directly "
        "when those adjustments are known. Medicare deductions remain unmodeled."
    )
    reference = (
        # Section 1.9; minor-earnings/lump-sum conflicts documented.
        "https://dfs.wyo.gov/wp-content/uploads/2025/10/FFY2026-LIEAP-State-Model-Plan.pdf#page=6",
        # Current chapter 1, section 8(a), PDF pages 11-13.
        "https://rules.wyo.gov/Search.aspx?mode=7",
    )
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wy.dfs.lieap.income
        person = spm_unit.members
        # Supplied net business income approximates allowable expenses.
        # Separate business and rental losses cannot offset positive sources.
        earned = sum(max_(person(source, period), 0) for source in p.earned_sources)
        support_paid = max_(person("child_support_expense", period), 0)
        # The input does not identify court orders or monthly regularity.
        # Deduct only from this payer's earnings, never another member's.
        earned = where(
            person("age", period) >= p.earned_income_min_age,
            max_(earned - support_paid, 0),
            0,
        )
        unearned = sum(max_(person(source, period), 0) for source in p.unearned_sources)
        # These are thresholds, not deductions. Annualization assumes
        # constant monthly receipts; interest and gifts are assessed separately.
        interest = max_(person("interest_income", period), 0)
        gifts = max_(person("financial_assistance", period), 0)
        countable_interest = where(
            interest > p.interest_monthly_threshold * MONTHS_IN_YEAR, interest, 0
        )
        countable_gifts = where(
            gifts > p.gift_monthly_threshold * MONTHS_IN_YEAR, gifts, 0
        )
        guideline = spm_unit("wy_lieap_fpg", period)
        # Approved approximation: total VA income, one exclusion per SPM unit.
        # Do not apply a separate allowance to each veteran, spouse or dependent.
        veterans = spm_unit.sum(max_(person("veterans_benefits", period), 0))
        veterans_exclusion = guideline * p.veterans_fpg_rate
        countable_veterans = max_(veterans - veterans_exclusion, 0)
        return (
            spm_unit.sum(earned + unearned + countable_interest + countable_gifts)
            + countable_veterans
        )
