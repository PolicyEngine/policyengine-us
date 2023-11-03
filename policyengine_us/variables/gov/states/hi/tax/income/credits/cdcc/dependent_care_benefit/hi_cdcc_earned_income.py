from policyengine_us.model_api import *


class hi_cdcc_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Hawaii eligible income floor"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=28"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=29"
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=41"
        "https://files.hawaii.gov/tax/forms/2022/schx_i.pdf#page=2"
    )

    def formula(person, period, parameters):
        # Head or spouse are eligible for an income floor if disabled or a student
        income_floor_eligible = person("is_disabled", period) | person(
            "is_full_time_student", period
        )
        income = person("earned_income", period)
        increased_income = person("hi_cdcc_eligible_income_floor", period)
        uncapped_income = where(
            income_floor_eligible,
            increased_income,
            income,
        )
        # Edge case: both spouses were students or disabled:
        # If both filers are disabled / student below the floor limit,
        # only one person with larger earning gets elevated to the floor
        # If both filers are disabled / student but only one person is below the floor limit,
        # then the person below the floor limit will be elevated to the floor
        below_income_floor = income_floor_eligible & (income < uncapped_income)
        head_spouse_income = where(
            sum(below_income_floor) > 1,
            min_(income, uncapped_income),
            uncapped_income,
        )

        return head_spouse_income
