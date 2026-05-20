from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class wv_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia Child and Dependent Care Credit"
    unit = USD
    defined_for = StateCode.WV
    definition_period = YEAR
    reference = "https://code.wvlegislature.gov/11-21-26/"

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.wv.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "wv_income_tax_before_non_refundable_credits",
            "wv_cdcc",
            "wv_cdcc_potential",
        )
