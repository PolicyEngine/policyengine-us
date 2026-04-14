from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class me_non_refundable_child_care_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine non-refundable child care credit"
    unit = USD
    documentation = "The portion of the Maine Child Care Credit that is non-refundable."
    reference = [
        "https://www.mainelegislature.org/legis/statutes/36/title36sec5218.html",
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_a_ff.pdf#page=2",
    ]
    definition_period = YEAR
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.me.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "me_income_tax_before_credits",
            "me_non_refundable_child_care_credit",
            "me_non_refundable_child_care_credit_potential",
        )
