from policyengine_us.model_api import *


class oh_retirement_income_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Retirement Income Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5747.055"
    defined_for = "oh_retirement_income_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.oh.tax.income.credits.retirement_income

        person = tax_unit.members
        is_spouse = person("is_tax_unit_spouse", period)
        is_head = person("is_tax_unit_head", period)
        pension_income = person("pension_income", period)
        has_not_taken_lump_sum_distribution = person(
            "oh_has_not_taken_oh_lump_sum_credits", period
        )
        head_or_spouse = is_head | is_spouse
        eligible_pension = (
            pension_income
            * has_not_taken_lump_sum_distribution
            * head_or_spouse
        )
        total_pension_income = tax_unit.sum(eligible_pension)

        return p.amount.calc(total_pension_income, right=True)
