from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class wi_blind_worker_transportation_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin blind-worker transportation credit on the standard tax path"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WI
    documentation = (
        "Credit applied to the liability remaining after earlier credits on the "
        "standard Wisconsin tax path. This intermediate amount is not the credit "
        "claimed on the chosen return when the retirement income exclusion is "
        "elected. Final Wisconsin income tax retains the separate path selection."
    )
    reference = (
        # PDF pages 20, 56, 58.
        "https://docs.legis.wisconsin.gov/statutes/statutes/71.pdf#page=20",
        # PDF pages 17-18.
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-inst.pdf#page=17",
    )

    def formula_2024_01_01(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.wi.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "wi_income_tax_before_credits",
            "wi_blind_worker_transportation_credit",
            "wi_blind_worker_transportation_credit_potential",
        )
