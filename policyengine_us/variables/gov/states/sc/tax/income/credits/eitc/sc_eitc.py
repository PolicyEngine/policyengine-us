from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class sc_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina EITC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.sc.gov/forms-site/Forms/TC60_2021.pdf",
        "https://www.scstatehouse.gov/sess126_2025-2026/bills/4216.htm",
    )
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.sc.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "sc_income_tax_before_non_refundable_credits",
            "sc_eitc",
            "sc_eitc_potential",
        )
