from policyengine_us.model_api import *


class hi_cdcc_min_head_spouse_earned(Variable):
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
        # Head or spouse are eligible for an income floor if disabled or a student
        # income_floor_eligible = person("is_disabled", period) | person(
        #     "is_full_time_student", period
        # )
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        income = person("earned_income", period) 
        dependent_excluded_income = where(head_or_spouse, income, np.inf)
        income_floor = tax_unit.max(person("hi_cdcc_eligible_income_floor", period))
        total_income_floor_eligible_people = tax_unit.sum(income_floor)
        # Edge case: both spouses were students or disabled:
        # If both filers are disabled / student below the floor limit,
        # only one person with larger earning gets elevated to the floor
        # If both filers are disabled / student but only one person is below the floor limit,
        # then the person below the floor limit will be elevated to the floor
        smaller_earnings = tax_unit.min(dependent_excluded_income)
        return where(total_income_floor_eligible_people == 1, income_floor, smaller_earnings)
