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
        # Edge case: both spouses were students or disabled:
        # If both filers are disabled / student below the floor limit,
        # only one person with larger earning gets elevated to the floor
        # If both filers are disabled / student but only one person is below the floor limit,
        # then the person below the floor limit will be elevated to the floor
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        income = person("earned_income", period)
        dependent_excluded_income = where(head_or_spouse, income, np.inf)
        income_floor_lst = person("hi_cdcc_eligible_income_floor", period)
        income_floor = tax_unit.max(income_floor_lst)
        income_floor_eligible_people = (
            head_or_spouse
            & (income_floor_lst != 0)
            & (dependent_excluded_income < income_floor)
        )
        income_below_floor = sum(dependent_excluded_income < income_floor)
        only_one_eligible = sum(income_floor_eligible_people) == 1
        only_one_eligible_below_floor = only_one_eligible & (
            income_below_floor >= 1
        )
        income_applied_floor = where(
            income_floor_eligible_people,
            income_floor,
            dependent_excluded_income,
        )
        return where(
            only_one_eligible_below_floor,
            tax_unit.min(income_applied_floor),
            tax_unit.min(dependent_excluded_income),
        )
