from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class va_non_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia non-refundable EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=32"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.va.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "va_income_tax_before_non_refundable_credits",
            "va_non_refundable_eitc",
            "va_non_refundable_eitc_potential",
        )
