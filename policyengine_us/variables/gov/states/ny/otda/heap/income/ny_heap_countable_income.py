from policyengine_us.model_api import *


class ny_heap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP annualized countable household income"
    unit = USD
    defined_for = StateCode.NY
    reference = (
        # PDF pages 36, 37, 38, 39, 40, 41, 42, 43, 44.
        "https://otda.ny.gov/programs/heap/HEAP-manual.pdf#page=37",
    )
    documentation = (
        "Annual inputs approximate application-month income; final monthly income is "
        "rounded down and annualized. Income of nonqualified members counts in full. "
        "Social Security and railroad benefits are counted net of the computed "
        "Medicare Part B premium; Part D has no variable and stays gross. Each "
        "unearned source is floored at zero, so a rental or estate loss does not "
        "offset other income. Royalties, regular gifts, aid-and-attendance "
        "exclusions and irregular-income exclusions cannot be isolated reliably. No "
        "new self-employment or work-expense deduction is applied."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.otda.heap.income
        person = spm_unit.members
        # Chapter 8 D.4 excludes foster members and federal Code C SSI
        # recipients. Nonqualified members are excluded only from household
        # size; their income still counts in full under D.4(a)(7).
        included = ~person("ny_heap_is_excluded_person", period)
        # D.14(b)(7) (page 41) converts negative income to zero and lists net
        # loss as a deduction that is not allowed, so each source is floored
        # like the earned sources: a loss in one source cannot offset another.
        unearned = 0
        for source in p.sources.unearned:
            unearned = unearned + max_(person(source, period), 0)
        # D.12(a)(6) and (8) (page 38) count Social Security and railroad
        # benefits after the Medicare Part B and D premiums. The computed
        # medicare_part_b_premium is the out-of-pocket Part B premium, zero when
        # a Medicare Savings Program pays it; no Part D variable exists.
        benefits = max_(
            person("social_security", period)
            + person("railroad_benefits", period)
            - person("medicare_part_b_premium", period),
            0,
        )
        income = spm_unit.sum(
            (person("ny_heap_countable_earned_income", period) + unearned + benefits)
            * included
        )
        # TANF is not counted: FY2026 State Plan item 1.9 (page 6) leaves the
        # TANF box unchecked, and Chapter 8 D.11(c)(1) (page 37) counts a TA
        # grant only for a minor child budgeted as a roomer, which has no input.
        return np.floor(income / MONTHS_IN_YEAR) * MONTHS_IN_YEAR
