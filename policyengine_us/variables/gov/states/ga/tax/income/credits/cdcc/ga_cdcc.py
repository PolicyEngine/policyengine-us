from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ga_cdcc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia non-refundable dependent care credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        # Georgia matches the federal credit taken
        federal_cdcc = tax_unit("cdcc", period)
        rate = parameters(period).gov.states.ga.tax.income.credits.cdcc.rate
        return federal_cdcc * rate


class ga_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia non-refundable dependent care credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ga.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "ga_income_tax_before_non_refundable_credits",
            "ga_cdcc",
            "ga_cdcc_potential",
        )
