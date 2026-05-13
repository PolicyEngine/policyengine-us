from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class la_non_refundable_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana non-refundable Child and Dependent Care Credit"
    unit = USD
    definition_period = YEAR
    reference = "http://legis.la.gov/Legis/Law.aspx?d=101769"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.la.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "la_income_tax_before_non_refundable_credits",
            "la_non_refundable_cdcc",
            "la_non_refundable_cdcc_potential",
        )
