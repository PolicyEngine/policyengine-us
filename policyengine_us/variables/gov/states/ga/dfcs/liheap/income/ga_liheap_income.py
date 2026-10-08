from policyengine_us.model_api import *


class ga_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Georgia LIHEAP annual countable household income"
    defined_for = StateCode.GA
    reference = (
        # The manual is followed where the plan conflicts.
        # PDF pages 62-69
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/GA_PolicyManual_2023.pdf#page=62",
        # PDF pages 5-6
        "https://liheapch.acf.gov/docs/2026/state-plans/GA_Plan_2026.pdf#page=5",
        # Section 1.9: Social Security "Excluding MediCare deduction".
        "https://liheapch.acf.gov/docs/2025/state-plans/GA_Plan_2025.pdf#page=6",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.dfcs.liheap.income
        person = spm_unit.members
        adult = person("age", period) >= p.minimum_age
        # Annual inputs approximate income in the application period. Georgia
        # excludes all income of under-18s, not only their earnings, and counts
        # otherwise countable income of nonqualified adults in full.
        # Manual sections 1200.6-1200.7 (pages 64-66) net self-employment and
        # farm income within the business and count capital gains, not losses,
        # so each source is floored at zero and a loss in one source cannot
        # offset another.
        person_income = 0
        for source in p.sources.person:
            person_income = person_income + max_(person(source, period), 0)
        # Plan section 1.9 (FY2025 and FY2026) counts Social Security
        # "Excluding MediCare deduction", and manual section 1200.7 (page 69)
        # excludes the premiums. medicare_part_b_premium is zero for a person
        # who is not enrolled and excludes the share a Medicare Savings
        # Program pays, which is not withheld from the check.
        premium = person("medicare_part_b_premium", period)
        social_security = max_(person("social_security", period) - premium, 0)
        adult_income = spm_unit.sum((person_income + social_security) * adult)
        adult_interest = spm_unit.sum(person("interest_income", period) * adult)
        # The manual excludes the first $25 of monthly interest without saying
        # this allowance repeats per person or account. Apply it once to the
        # household's adult interest; dividends remain fully countable.
        interest = max_(
            adult_interest - p.monthly_interest_disregard * MONTHS_IN_YEAR,
            0,
        )
        # TANF is included once at SPM level as a caregiver grant rather than
        # projecting the household award onto every member.
        household_income = add(spm_unit, period, p.sources.household)
        # Roomer/boarder expense allowances, mortgage-sale contracts and stipends
        # lack scoped handling. Cash contributions use financial_assistance;
        # gifts and lottery winnings follow the detailed manual (see sources).
        return adult_income + interest + household_income
