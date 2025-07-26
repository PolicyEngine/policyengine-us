from policyengine_us.model_api import *


class pr_mortgage_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico home mortgage deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/"  # (1)(C)
    defined_for = StateCode.PR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.deductions.mortgage

        agi = tax_unit("pr_agi", period)
        limit = agi * p.floor  # plus any income excluded from AGI

        mortgage_interest = add(
            tax_unit, period, ["deductible_mortgage_interest"]
        )
        person = tax_unit.members
        age = person("age", period)

        is_senior_exception = tax_unit.any(
            person("is_tax_unit_head_or_spouse", period)
            & (age >= p.age_threshold)
        )
        # True if any member fulfills condition

        # people 65+ years old are capped at max deduction amount
        interest_capped_by_max = min_(mortgage_interest, p.max)
        # otherwise capped by both AGI and max deduction amount
        combined_cap = min_(limit, p.max)
        interest_capped_by_combined = min_(mortgage_interest, combined_cap)
        return where(
            is_senior_exception,
            interest_capped_by_max,
            interest_capped_by_combined,
        )
