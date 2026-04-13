from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ny_household_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY household credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (b)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ny.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "ny_income_tax_before_credits",
            "ny_household_credit",
            "ny_household_credit_potential",
        )
