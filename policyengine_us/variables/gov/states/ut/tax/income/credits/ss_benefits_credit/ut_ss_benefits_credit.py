from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ut_ss_benefits_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah Social Security Benefits Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ut.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "ut_income_tax_before_non_refundable_credits",
            "ut_ss_benefits_credit",
            "ut_ss_benefits_credit_potential",
        )
