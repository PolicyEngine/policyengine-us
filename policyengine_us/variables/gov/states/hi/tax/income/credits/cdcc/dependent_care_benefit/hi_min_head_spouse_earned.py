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
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = head | spouse
        # Head or spouse are eligible for an income floor if disabled or a student
        income_floor_eligible = head_or_spouse & (
            person("is_disabled", period)
            | person("is_full_time_student", period)
        )
        income = person("earned_income", period)
        # increased_income = max_(head_or_spouse_income, income_floor)
        increased_income = person("hi_eligible_income_floor", period)
        uncapped_income = where(
            income_floor_eligible,
            increased_income,
            income,
        )
        # remove impact of income for dependents
        head_spouse_income = where(
            head_or_spouse, uncapped_income, tax_unit.max(uncapped_income)
        )
        # Edge case: both spouses were students or disabled:
        # If both filers are disabled / student below the floor limit,
        # only one person with larger earning gets elevated to the floor
        # If both filers are disabled / student but only one person is below the floor limit,
        # then the person below the floor limit will be elevated to the floor
        reach_income_floor = income < uncapped_income
        head_spouse_income = where(
            (sum(income_floor_eligible) == 2) & (sum(reach_income_floor) > 1),
            min_(income, uncapped_income),
            head_spouse_income,
        )
        return tax_unit.min(head_spouse_income)
