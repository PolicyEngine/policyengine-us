from policyengine_us.model_api import *


class mt_interest_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana interest exemptions"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=25"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions.interest
        filing_status = tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        person = tax_unit.members
        dividend_income = add(person, period, ["taxable_interest_income"])
        dividend_income_unit = tax_unit.sum(dividend_income)
        capped_amount = min_(cap, dividend_income_unit)
        age_head = tax_unit("age_head", period)
        eligible_aged_head = age_head >= p.age
        age_spouse = tax_unit("age_spouse", period)
        eligible_aged_spouse = age_spouse >= p.age
        eligible_tax_unit = eligible_aged_head | eligible_aged_spouse
        return eligible_tax_unit * capped_amount
