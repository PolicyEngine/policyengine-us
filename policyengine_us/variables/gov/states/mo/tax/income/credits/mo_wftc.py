from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class mo_wftc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri Working Families Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.177&bid=49978&hl="
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.mo.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "mo_income_tax_before_credits",
            "mo_wftc",
            "mo_wftc_potential",
        )
