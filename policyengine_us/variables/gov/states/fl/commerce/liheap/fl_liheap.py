from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class fl_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Florida LIHEAP regular heating assistance"
    defined_for = StateCode.FL
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/FL_BenefitMatrix_Heat-Cool_2026.pdf",
        # PDF pages 8-9, 23-24, 43
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/FL_PolicyManual_2023.pdf#page=8",
        "https://liheapch.acf.gov/docs/2026/state-plans/FL_Plan_2026.pdf#page=9",
        "https://liheapch.acf.gov/docs/2025/benefits-matricies/FL_BenefitMatrix_2025.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.commerce.liheap
        income = spm_unit("fl_liheap_countable_income", period)
        limit = spm_unit("fl_liheap_income_limit", period)
        size = spm_unit("fl_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            size,
            state_group,
            period,
            parameters,
            year_lag=p.eligibility.fpg_year_lag,
        )
        # Where the poverty-guideline limit sets the maximum income value
        # (FY2025 sizes 9 and above), the bands are guideline percentages.
        fpg_based = guideline * p.eligibility.fpg_rate >= limit
        fraction = p.payment.income_band_fraction
        band_fpg_rate = p.payment.income_band_fpg_rate
        # Half-up dollar cutoffs reproduce the printed bands without leaving
        # gaps for income with cents between successive printed dollar bounds.
        first = where(
            fpg_based,
            guideline * band_fpg_rate.first,
            np.floor(limit * fraction.first + 0.5),
        )
        second = where(
            fpg_based,
            guideline * band_fpg_rate.second,
            np.floor(limit * fraction.second + 0.5),
        )
        third = where(
            fpg_based,
            guideline * band_fpg_rate.third,
            np.floor(limit * fraction.third + 0.5),
        )
        # The operative matrix publishes a distinct FY2026 size-13 row.
        # Its band cutoffs govern payments even though its printed maximum
        # conflicts with the plan's 60%-SMI eligibility ceiling.
        published_row = size == p.payment.published_band_size
        published = p.payment.published_band_upper_bound
        first = where(published_row, published.first, first)
        second = where(published_row, published.second, second)
        third = where(published_row, published.third, third)
        # The FY2025 second guideline band starts "At least 75%" of the
        # guideline, so the first guideline band excludes its upper bound.
        in_first = where(fpg_based, income < first, income <= first)
        band = select(
            [in_first, income <= second, income <= third],
            [1, 2, 3],
            default=4,
        )
        # Categorical households above the printed maximum use the smallest
        # base as an estimate; sources waive the income test but do not supply
        # an above-range benefit band. Receipt alone never selects a top band.
        base = p.payment.base_amount[band]
        age = spm_unit.members("age", period)
        elderly = spm_unit.any(age >= p.payment.elderly_min_age)
        disabled = add(spm_unit, period, ["is_disabled"]) > 0
        child = spm_unit.any(age < p.payment.child_max_age + 1)
        supplement = p.payment.supplement
        supplements = (
            elderly * supplement.elderly
            + disabled * supplement.disabled
            + child * supplement.child
        )
        # FY2026 follows the operative October 2025 matrix ($200-$700), as
        # required by the manual; the FY2026 plan's estimated $400-$1,350
        # extrema conflict with it. The FY2025 plan and matrix agree.
        # One award per year is modeled. No actual-bill cap or HUD deduction
        # applies to regular benefits; previous awards require unavailable data.
        eligible = spm_unit("fl_liheap_eligible", period)
        return eligible * (base + supplements)
