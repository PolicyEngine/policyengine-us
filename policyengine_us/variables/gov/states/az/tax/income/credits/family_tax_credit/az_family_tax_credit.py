from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class az_family_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Family Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "az_family_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.az.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "az_income_tax_before_non_refundable_credits",
            "az_family_tax_credit",
            "az_family_tax_credit_potential",
        )
