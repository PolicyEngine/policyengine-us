from policyengine_us.model_api import *


class mt_interest_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana interest exemption for the tax unit"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=25"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions.interest
        filing_status = tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        interest_income = (
            person("taxable_interest_income", period) * head_or_spouse
        )
        total_interest_income = tax_unit.sum(interest_income)
        return min_(cap, total_interest_income)
