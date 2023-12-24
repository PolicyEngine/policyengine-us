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
        tax_before_joint_filing_crdedit = tax_unit(
            "oh_tax_before_joint_filing_credit", period
        )
        p = parameters(period).gov.states.oh.tax.income.credits.joint_filing
        # Ohio use MAGI for the credit computation, which is Ohio AGI with
        # the addition of the business income deduction, which is currently not included in the model
        # hence, we use Ohio AGI for the credit computation
        oh_agi = tax_unit("oh_agi", period)
        exemption = tax_unit("oh_exemptions", period)
        agi_less_exepmtion = max_(oh_agi - exemption, 0)
        percentage = p.rate.calc(agi_less_exepmtion)
        return min_(tax_before_joint_filing_crdedit * percentage, p.cap)
