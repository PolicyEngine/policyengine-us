from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class il_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois Property Tax Credit"
    unit = USD
    definition_period = YEAR

    defined_for = "il_is_exemption_eligible"

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.il.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "il_income_tax_before_non_refundable_credits",
            "il_property_tax_credit",
            "il_property_tax_credit_potential",
        )
