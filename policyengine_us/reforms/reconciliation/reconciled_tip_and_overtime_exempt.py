from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_reconciled_tip_and_overtime_exempt() -> Reform:
    class tip_income_ald(Variable):
        value_type = float
        entity = TaxUnit
        label = "Itemized taxable income deductions reduction"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.reconciliation.tip_income_exempt
            if p.in_effect:
                return add(tax_unit, period, ["tip_income"])
            return 0

    class overtime_income_ald(Variable):
        value_type = float
        entity = TaxUnit
        label = "Overtime income ALD"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.reconciliation.overtime_income_exempt
            if p.in_effect:
                return add(tax_unit, period, ["overtime_income"])
            return 0

    def modify_parameters(parameters):
        parameters.gov.irs.deductions.deductions_if_itemizing.update(
            start=instant("2026-01-01"),
            stop=instant("2035-12-31"),
            value=[
                "tip_income_ald",
                "overtime_income_ald",
                "charitable_deduction",
                "interest_deduction",
                "salt_deduction",
                "medical_expense_deduction",
                "casualty_loss_deduction",
                "qualified_business_income_deduction",
                "wagering_losses_deduction",
                "misc_deduction",
            ],
        )
        parameters.gov.irs.deductions.deductions_if_not_itemizing.update(
            start=instant("2026-01-01"),
            stop=instant("2035-12-31"),
            value=[
                "tip_income_ald",
                "overtime_income_ald",
                "standard_deduction",
                "qualified_business_income_deduction",
            ],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(tip_income_ald)
            self.update_variable(overtime_income_ald)
            self.modify_parameters(modify_parameters)

    return reform


def create_reconciled_tip_and_overtime_exempt_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_reconciled_tip_and_overtime_exempt()

    p = parameters.gov.contrib.reconciliation

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if (
            p(current_period).tip_income_exempt.in_effect
            or p(current_period).overtime_income_exempt.in_effect
        ):
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_reconciled_tip_and_overtime_exempt()
    else:
        return None


reconciled_tip_and_overtime_exempt = (
    create_reconciled_tip_and_overtime_exempt_reform(None, None, bypass=True)
)
