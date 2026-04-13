from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ri_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island child and dependent care credit"
    defined_for = StateCode.RI
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ri.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "ri_income_tax_before_non_refundable_credits",
            "ri_cdcc",
            "ri_cdcc_potential",
        )
