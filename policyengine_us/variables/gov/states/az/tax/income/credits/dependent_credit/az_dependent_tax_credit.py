from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class az_dependent_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona dependent tax credit"
    unit = USD
    documentation = "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01073-01.htm"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.az.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "az_income_tax_before_non_refundable_credits",
            "az_dependent_tax_credit",
            "az_dependent_tax_credit_potential",
        )
