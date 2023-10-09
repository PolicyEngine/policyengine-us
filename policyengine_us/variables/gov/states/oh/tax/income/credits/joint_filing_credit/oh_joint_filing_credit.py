from policyengine_us.model_api import *


class oh_joint_filing_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Joint Filing Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5747.05"
    defined_for = "oh_joint_filing_credit_eligible"

    def formula(tax_unit, period, parameters):
        tax = tax_unit("oh_income_tax_before_refundable_credits", period)
        p = parameters(
            period
        ).gov.states.oh.tax.income.credits.joint_filing_credit
        oh_agi = tax_unit("oh_agi", period)
        exemption = tax_unit("oh_exemptions", period)
        magi_less_exepmtion = max_(oh_agi - exemption, 0)
        percentage = p.rate.calc(magi_less_exepmtion)
        return min_(tax * percentage, p.max_amount)
