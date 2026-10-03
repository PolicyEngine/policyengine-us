from policyengine_us.model_api import *


class ga_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Georgia LIHEAP annual countable household income"
    defined_for = StateCode.GA
    reference = (
        # Manual pages 62-69; current plan pages 5-6 govern listed exclusions.
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/GA_PolicyManual_2023.pdf#page=62",
        "https://liheapch.acf.gov/docs/2026/state-plans/GA_Plan_2026.pdf#page=5",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.dfcs.liheap.income
        person = spm_unit.members
        adult = person("age", period) >= p.minimum_age
        # Annual inputs approximate income in the application period. Georgia
        # excludes all income of under-18s, not only their earnings, and counts
        # otherwise countable income of nonqualified adults in full.
        person_income = add(person, period, p.sources.person, options=[ADD])
        adult_interest = spm_unit.sum(person("interest_income", period) * adult)
        # The manual excludes the first $25 of monthly interest without saying
        # this allowance repeats per person or account. Apply it once to the
        # household's adult interest; dividends remain fully countable.
        interest = max_(
            adult_interest - p.monthly_interest_disregard * MONTHS_IN_YEAR,
            0,
        )
        # State TANF is included once at SPM level as a caregiver grant rather
        # than projecting the household award onto every member.
        household_income = add(spm_unit, period, p.sources.household, options=[ADD])
        # Keep existing signed net business inputs without another deduction;
        # floor the combined total. Rental income is assumed nonnegative.
        # Roomer/boarder expense allowances, Medicare premiums, mortgage-sale
        # contracts, stipends, and recurring support lack the scoped handling.
        # Current plan exclusions govern cash gifts and lump-sum receipts.
        return max_(
            spm_unit.sum(person_income * adult) + interest + household_income,
            0,
        )
