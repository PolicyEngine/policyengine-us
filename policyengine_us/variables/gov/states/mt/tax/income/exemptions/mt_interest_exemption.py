from policyengine_us.model_api import *


class mt_interest_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana interest exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=25"
    defined_for = "mt_interest_exemption_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions.interest
        filing_status = tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        interest_income = add(tax_unit, period, ["taxable_interest_income"])
        eligible_amount = min_(cap, interest_income)
        eligible_person = tax_unit("mt_interest_exemption_eligible", period)
        return eligible_person * eligible_amount
