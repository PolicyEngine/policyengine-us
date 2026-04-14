from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ms_charitable_contributions_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi charitable contributions credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100211_0.pdf#page=18",
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100231.pdf#page=3",
    )

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ms.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "ms_income_tax_before_credits_unit",
            "ms_charitable_contributions_credit",
            "ms_charitable_contributions_credit_potential",
        )
