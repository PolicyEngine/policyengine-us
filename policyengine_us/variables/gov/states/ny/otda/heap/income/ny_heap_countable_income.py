from policyengine_us.model_api import *


class ny_heap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP annualized countable household income"
    unit = USD
    defined_for = StateCode.NY
    reference = (
        "https://otda.ny.gov/programs/heap/HEAP-manual.pdf#page=37,38,39,40,41,42,43,44",
    )
    documentation = "Annual inputs approximate application-month income; final monthly income is rounded down and annualized. Income of nonqualified members counts in full. Medicare Part D premiums, royalties, regular gifts, aid-and-attendance exclusions and irregular-income exclusions have no dedicated inputs. Rental income is assumed nonnegative. No new self-employment or work-expense deduction is applied."

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.otda.heap.income
        person = spm_unit.members
        retirement = add(person, period, ["social_security", "railroad_benefits"])
        net_retirement = spm_unit.sum(
            max_(retirement - person("medicare_part_b_premium", period), 0)
        )
        income = (
            add(spm_unit, period, ["ny_heap_countable_earned_income"])
            + add(spm_unit, period, p.sources.unearned)
            + net_retirement
        )
        return np.floor(max_(income, 0) / MONTHS_IN_YEAR) * MONTHS_IN_YEAR
