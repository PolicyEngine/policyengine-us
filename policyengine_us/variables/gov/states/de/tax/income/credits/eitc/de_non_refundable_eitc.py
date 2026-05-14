from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class de_non_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware non-refundable EITC"
    unit = USD
    documentation = "Non-refundable EITC credit reducing DE State income tax."
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf"
    )
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.de.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "de_income_tax_before_non_refundable_credits_unit",
            "de_non_refundable_eitc",
            "de_non_refundable_eitc_potential",
        )
