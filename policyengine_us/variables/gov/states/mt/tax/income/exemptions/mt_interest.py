from policyengine_us.model_api import *


class mt_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana exemptions amount"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=25"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions
        filing_status = tax_unit("filing_status", period)
        cap_amount = p.amount[filing_status]
        dividend_income = tax_unit(
            "taxsim_dividends", period
        )  # dividends or share accounts
        qalified_amount = min_(cap_amount, dividend_income)
        age_head = tax_unit("age_head", period)
        eligible_aged_head = age_head >= p.age
        age_spouse = tax_unit("age_spouse", period)
        eligible_aged_spouse = age_spouse >= p.age
        eligible_tax_unit = eligible_aged_head | eligible_aged_spouse
        return where(eligible_tax_unit, qalified_amount, 0)
