from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)

class oh_joint_filing_credit_potential(Variable):
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


class oh_joint_filing_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio joint filing credit"
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5747.05"
    defined_for = "oh_joint_filing_credit_eligible"

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.oh.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "oh_income_tax_before_non_refundable_credits",
            "oh_joint_filing_credit",
            "oh_joint_filing_credit_potential",
        )
