from policyengine_us.model_api import *


class hi_min_head_spouse_earned(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii minimum income between head and spouse for the CDCC"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=28"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=29"
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=41"
        "https://files.hawaii.gov/tax/forms/2022/schx_i.pdf#page=2"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.cdcc
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = head | spouse
        # Head or spouse are eligible for an income floor if disabled or a student
        income_floor_eligible = head_or_spouse & (
            person("is_disabled", period)
            | person("is_full_time_student", period)
        )
        qualified_children = tax_unit("count_cdcc_eligible", period)

        # Floor depends on number of eligible dependents
        income_floor = p.disabled_student_income_floor.calc(qualified_children)
        income = person("earned_income", period)
        head_or_spouse_income = head_or_spouse * income
        increased_income = max_(head_or_spouse_income, income_floor)
        uncapped_income = where(
            income_floor_eligible,
            increased_income,
            head_or_spouse_income,
        )
        # remove impact of 0 income output for dependents
        head_spouse_income = where(
            head_or_spouse, uncapped_income, tax_unit.max(uncapped_income)
        )
        # Edge case: both spouses were students or disabled:
        # compare original income with eligible income
        both_disabled_income = where(
            head_or_spouse,
            min_(head_or_spouse_income, uncapped_income),
            head_spouse_income,
        )
        # If both filers are disabled / student below the floor limit,
        # only one person gets elevated to the floor
        # If both filers are disabled / student but only one person is below the floor limit,
        # then the person with the lower earnings will be elevated to the floor
        reach_income_floor = head_or_spouse_income < uncapped_income
        head_spouse_income = where(
            (sum(income_floor_eligible) == 2) & (sum(reach_income_floor) == 2),
            both_disabled_income,
            head_spouse_income,
        )
        return tax_unit.min(head_spouse_income)
