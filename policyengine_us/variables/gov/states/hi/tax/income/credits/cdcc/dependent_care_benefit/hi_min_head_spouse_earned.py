from policyengine_us.model_api import *


class hi_min_head_spouse_earned(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii minimum income between head and spouse"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=27"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.cdcc
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        disabled = tax_unit.any(
            (head | spouse) & person("is_disabled", period)
        )
        full_time_student = tax_unit.any(
            (head | spouse) & person("is_full_time_student", period)
        )
        min_income_eligible = disabled | full_time_student
        income = person("earned_income", period)
        head_income = tax_unit.sum(head * income)
        spouse_income = select(
            [
                sum(spouse) > 0,
                sum(spouse) == 0,
            ],
            [
                tax_unit.sum(spouse * income),
                head_income,
            ],
        )

        qualified_num = tax_unit("count_cdcc_eligible", period)
        # Note: married persons must file a joint return to claim the credit
        min_income = select(
            [
                min_income_eligible & (qualified_num <= 1),
                min_income_eligible & (qualified_num > 1),
                ~min_income_eligible,
            ],
            [
                min_(max_(head_income, 2400), max_(spouse_income, 2400)),
                min_(max_(head_income, 4800), max_(spouse_income, 4800)),
                min_(head_income, spouse_income),
            ],
        )

        return min_income
