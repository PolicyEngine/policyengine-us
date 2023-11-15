from policyengine_us.model_api import *


class vt_charitable_contribution_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont charitable contribution credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/vermont/2022/title-32/chapter-151/section-5822/"
        "https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf#page=1"
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        charitable_deduction = tax_unit("charitable_deduction", period)
        p = parameters(period).gov.states.vt.tax.income.credits.charitable
        credit_amount = p.rate * charitable_deduction
        capped_credit_amount = p.rate * p.cap
        return min_(credit_amount, capped_credit_amount)
