from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)

class de_cdcc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware dependent care credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        # Delaware matches the federal credit taken
        expenses = tax_unit("cdcc", period)
        rate = parameters(period).gov.states.de.tax.income.credits.cdcc.match
        return expenses * rate


class de_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware dependent care credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.de.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "de_income_tax_before_non_refundable_credits_unit",
            "de_cdcc",
            "de_cdcc_potential",
        )
