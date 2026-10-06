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
        "Medicare-premium deductions remain deferred. Royalties, regular gifts, "
        "aid-and-attendance exclusions and irregular-income exclusions cannot be "
        "isolated reliably. Rental income is assumed nonnegative. No new "
        "self-employment or work-expense deduction is applied."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.otda.heap.income
        person = spm_unit.members
        # Chapter 8 D.4 excludes foster members and federal Code C SSI
        # recipients. Nonqualified members are excluded only from household
        # size; their income still counts in full under D.4(a)(7).
        included = ~person("ny_heap_is_excluded_person", period)
        income = spm_unit.sum(
            (
                person("ny_heap_countable_earned_income", period)
                + add(person, period, p.sources.unearned)
            )
            * included
        )
        # TANF is not counted: FY2026 State Plan item 1.9 (page 6) leaves the
        # TANF box unchecked, and Chapter 8 D.11(c)(1) (page 37) counts a TA
        # grant only for a minor child budgeted as a roomer, which has no input.
        # D.12(a)(6) (page 38) counts Social Security after Medicare Part B and
        # D premiums. medicare_part_b_premium and
        # medicare_part_b_premiums_reported are not wired in yet, so Social
        # Security counts gross.
        return np.floor(max_(income, 0) / MONTHS_IN_YEAR) * MONTHS_IN_YEAR
