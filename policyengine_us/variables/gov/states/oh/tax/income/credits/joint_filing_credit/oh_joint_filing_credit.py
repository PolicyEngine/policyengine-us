from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


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
