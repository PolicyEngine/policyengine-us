from policyengine_us.model_api import *


class oh_retirement_income_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Retirement Income Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5747.055"
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.oh.tax.income.credits.retirement_income

        person = tax_unit.members
        spouse = person("is_tax_unit_spouse", period)
        head = person("is_tax_unit_head", period)
        pension = person("pension_income", period)
        has_not_taken_lump_sum_distribution = person(
            "oh_has_not_taken_oh_lump_sum_credits", period
        )
        head_pension = head * pension * has_not_taken_lump_sum_distribution
        spouse_pension = spouse * pension * has_not_taken_lump_sum_distribution
        total_pension_income = tax_unit.sum(head_pension + spouse_pension)
        agi = tax_unit("oh_agi", period)
        eligible = agi < p.income_threshold

        return p.amount.calc(total_pension_income) * eligible
