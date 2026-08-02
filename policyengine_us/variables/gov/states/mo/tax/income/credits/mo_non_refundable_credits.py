from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    ordered_capped_state_non_refundable_credits,
)


class mo_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.mo.tax.income.credits.non_refundable
        # The aggregate caps against pre-credit tax; the Form MO-WFTC
        # line 8 netting of the property tax credit is specific to the
        # WFTC and applied in mo_wftc's own liability base.
        return ordered_capped_state_non_refundable_credits(
            tax_unit, period, ordered_credits, "mo_income_tax_before_credits"
        )
