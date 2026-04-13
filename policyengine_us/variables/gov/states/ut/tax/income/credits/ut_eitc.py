from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ut_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah Earned Income Tax Credit"
    unit = USD
    documentation = "This credit is a fraction of the federal EITC."
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1044.html?v=C59-10-S1044_2022050420220504"

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ut.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "ut_income_tax_before_non_refundable_credits",
            "ut_eitc",
            "ut_eitc_potential",
        )
