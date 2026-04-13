from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ga_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia Child Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA
    reference = (
        "https://legiscan.com/GA/text/HB136/id/3204611/Georgia-2025-HB136-Enrolled.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ga.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "ga_income_tax_before_non_refundable_credits",
            "ga_ctc",
            "ga_ctc_potential",
        )
