from policyengine_us.model_api import *


class oh_pension_based_retirement_income_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio pension based retirement income credit"
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5747.055"
    defined_for = "oh_pension_based_retirement_income_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.oh.tax.income.credits.retirement.pension_based

        person = tax_unit.members
        pension_income = person("taxable_pension_income", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        eligible_pension = pension_income * head_or_spouse
        total_pension_income = tax_unit.sum(eligible_pension)

        return p.amount.calc(total_pension_income, right=True)
