from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ar_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas Child and Dependent Care Credit"
    unit = USD
    documentation = (
        "https://codes.findlaw.com/ar/title-26-taxation/ar-code-sect-26-51-502/"
    )
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
            "ar_cdcc",
            "ar_cdcc_potential",
        )
