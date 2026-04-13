from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class oh_retirement_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Retirement Income Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5747.055"
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.oh.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "oh_income_tax_before_non_refundable_credits",
            "oh_retirement_credit",
            "oh_retirement_credit_potential",
        )
