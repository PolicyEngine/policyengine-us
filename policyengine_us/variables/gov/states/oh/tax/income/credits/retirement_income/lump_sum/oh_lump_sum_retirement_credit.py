from policyengine_us.model_api import *


class oh_lump_sum_retirement_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Lump Sum Retirement Income Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5747.055"  # (C, D, E)
    defined_for = "oh_lump_sum_retirement_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.credits.retirement

        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        pension_income = person("pension_income", period)
        age = person("age", period)
        age_eligible = age >= p.lump_sum.age_threshold

        divisor = p.lump_sum.divisor.calc(age)

        head_or_spouse_pension = head_or_spouse * pension_income

        head_or_spouse_credit = (
            p.pension_based.amount.calc(
                head_or_spouse_pension / divisor, right=True
            )
            * divisor
        )
        total_credit = where(divisor == 0, 0, head_or_spouse_credit)

        return tax_unit.sum(total_credit * age_eligible)
