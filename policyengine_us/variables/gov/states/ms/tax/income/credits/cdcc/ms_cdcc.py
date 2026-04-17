from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ms_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi child and dependent care credit"
    unit = USD
    definition_period = YEAR
    defined_for = "ms_cdcc_eligible"
    reference = "https://legiscan.com/MS/text/HB1671/id/2767768"

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ms.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "ms_income_tax_before_credits_unit",
            "ms_cdcc",
            "ms_cdcc_potential",
        )
