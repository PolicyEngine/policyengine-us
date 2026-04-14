from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class nc_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina credit for children"
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.ncdor.gov/taxes-forms/individual-income-tax/credit-children"
    )
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.nc.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "nc_income_tax_before_credits",
            "nc_ctc",
            "nc_ctc_potential",
        )
