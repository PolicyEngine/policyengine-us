from policyengine_us.model_api import *


class la_claim_of_right_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana claim of right repayment deduction"
    unit = USD
    documentation = (
        "A filer who reduces federal tax under 26 U.S.C. 1341(a)(5) deducts "
        "the amount repaid on Schedule E, because that method leaves federal "
        "adjusted gross income unchanged. Under section 1341(a)(4) the "
        "federal return already carries the deduction and Louisiana makes "
        "no adjustment."
    )
    definition_period = YEAR
    reference = (
        # Louisiana Revenue Ruling No. 04-002 (March 18, 2004)
        "https://dam.ldr.la.gov/lawspolicies/RR04002.pdf#page=1",
        # La. R.S. 47:295(B), the authority the ruling cites
        "https://www.legis.la.gov/legis/Law.aspx?d=101762",
    )
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        credit_applies = tax_unit("claim_of_right_credit_applies", period)
        repayment = tax_unit("tax_unit_claim_of_right_repayment", period)
        return where(credit_applies, repayment, 0)
