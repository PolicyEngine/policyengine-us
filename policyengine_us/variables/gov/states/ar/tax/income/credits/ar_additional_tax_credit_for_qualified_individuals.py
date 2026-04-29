from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ar_additional_tax_credit_for_qualified_individuals(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas additional tax credit for qualified individuals"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ar.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "ar_income_tax_before_non_refundable_credits_unit",
            "ar_additional_tax_credit_for_qualified_individuals",
            "ar_additional_tax_credit_for_qualified_individuals_potential",
        )
