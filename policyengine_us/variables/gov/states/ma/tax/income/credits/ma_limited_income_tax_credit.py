from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ma_limited_income_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Limited Income Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/doc/2021-schedule-nts-l-nrpy-no-tax-status-and-limited-income-credit/download"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ma.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "ma_income_tax_before_credits",
            "ma_limited_income_tax_credit",
            "ma_limited_income_tax_credit_potential",
        )
