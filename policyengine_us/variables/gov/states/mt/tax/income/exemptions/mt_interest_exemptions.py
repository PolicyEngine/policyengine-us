from policyengine_us.model_api import *


class mt_interest_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana exemptions amount"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=25"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions.interest
        filing_status = tax_unit("filing_status", period)
        cap_amount = p.amount[filing_status]
        person = tax_unit.members
        dividend_income = person(
            "dividend_income", period
        )  # dividends or share accounts
        dividend_income_unit = tax_unit.sum(dividend_income)
        qalified_amount = min_(cap_amount, dividend_income_unit)
        age_head = tax_unit("age_head", period)
        eligible_aged_head = age_head >= p.age
        age_spouse = tax_unit("age_spouse", period)
        eligible_aged_spouse = age_spouse >= p.age
        eligible_tax_unit = eligible_aged_head | eligible_aged_spouse
        return where(eligible_tax_unit, qalified_amount, 0)
