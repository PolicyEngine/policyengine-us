from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant
import numpy as np


def create_reconciled_charitable_deduction() -> Reform:
    class charitable_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Charitable deduction"
        unit = USD
        documentation = (
            "Deduction from taxable income for charitable donations."
        )
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/170"

        def formula(tax_unit, period, parameters):
            cash_donations = add(
                tax_unit, period, ["charitable_cash_donations"]
            )
            non_cash_donations = add(
                tax_unit, period, ["charitable_non_cash_donations"]
            )
            positive_agi = tax_unit("positive_agi", period)
            p = parameters(period).gov.irs.deductions.itemized.charity.ceiling
            p_ref = parameters(
                period
            ).gov.contrib.reconciliation.charitable_donations
            deduction_floor = p_ref.floor * positive_agi
            reduced_non_cash_donations = max_(
                non_cash_donations - deduction_floor, 0
            )
            capped_non_cash_donations = min_(
                reduced_non_cash_donations, p.non_cash * positive_agi
            )

            total_cap = p.all * positive_agi
            remaining_floor = max_(deduction_floor - non_cash_donations, 0)
            reduced_cash_donations = max_(cash_donations - remaining_floor, 0)
            return min_(
                capped_non_cash_donations + reduced_cash_donations, total_cap
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(charitable_deduction)

    return reform


def create_reconciled_charitable_deduction_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_reconciled_charitable_deduction()

    p = parameters.gov.contrib.reconciliation.charitable_donations

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_reconciled_charitable_deduction()
    else:
        return None


reconciliation_charitable_deduction = (
    create_reconciled_charitable_deduction_reform(None, None, bypass=True)
)
