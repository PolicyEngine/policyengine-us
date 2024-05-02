from policyengine_us.model_api import *


class oh_joint_filing_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio joint filing credit"
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5747.05"
    defined_for = "oh_joint_filing_credit_eligible"

    def formula(tax_unit, period, parameters):
        tax_before_joint_filing_credit = tax_unit(
            "oh_tax_before_joint_filing_credit", period
        )
        p = parameters(period).gov.states.oh.tax.income.credits.joint_filing
        # Ohio uses MAGI for the credit computation, which is Ohio AGI with
        # the addition of the business income deduction, which is currently not included in the model,
        # hence, we use the Ohio AGI for the credit computation
        oh_agi = tax_unit("oh_modified_agi", period)
        exemptions = tax_unit("oh_personal_exemptions", period)
        agi_less_exepmtions = max_(oh_agi - exemptions, 0)
        percentage = p.rate.calc(agi_less_exepmtions)
        return min_(tax_before_joint_filing_credit * percentage, p.cap)
