from policyengine_us.model_api import *


class fl_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Florida LIHEAP regular heating assistance"
    defined_for = StateCode.FL
    # Manual pages 8-9, 23-24 and 43; plan page 9.
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/FL_BenefitMatrix_Heat-Cool_2026.pdf",
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/FL_PolicyManual_2023.pdf#page=8",
        "https://liheapch.acf.gov/docs/2026/state-plans/FL_Plan_2026.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.commerce.liheap.payment
        income = spm_unit("fl_liheap_countable_income", period)
        limit = spm_unit("fl_liheap_income_limit", period)
        # Half-up dollar cutoffs reproduce the printed bands without leaving
        # gaps for income with cents between successive printed dollar bounds.
        first = np.floor(limit * p.income_band_fraction.first + 0.5)
        second = np.floor(limit * p.income_band_fraction.second + 0.5)
        third = np.floor(limit * p.income_band_fraction.third + 0.5)
        band = select(
            [income <= first, income <= second, income <= third],
            [1, 2, 3],
            default=4,
        )
        # Categorical households above the printed maximum use the smallest
        # base as an estimate; sources waive the income test but do not supply
        # an above-range benefit band. Receipt alone never selects a top band.
        base = p.base_amount[band]
        age = spm_unit.members("age", period)
        elderly = spm_unit.any(age >= p.elderly_min_age)
        disabled = spm_unit.any(spm_unit.members("is_disabled", period))
        child = spm_unit.any(age < p.child_max_age + 1)
        supplements = (
            elderly * p.supplement.elderly
            + disabled * p.supplement.disabled
            + child * p.supplement.child
        )
        # Follow the operative October 2025 matrix ($200-$700), as required by
        # the manual; the plan's estimated $400-$1,350 extrema conflict with it.
        # One award per year is modeled. No actual-bill cap or HUD deduction
        # applies to regular benefits; previous awards require unavailable data.
        eligible = spm_unit("fl_liheap_eligible", period)
        return eligible * (base + supplements)
