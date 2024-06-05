from policyengine_us.model_api import *


def create_il_child_tax_credit() -> Reform:
    class il_child_tax_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Illinois Child Tax Credit"
        unit = USD
        definition_period = YEAR
        reference = "https://www.niskanencenter.org/proposed-illinois-child-tax-credit-is-a-step-in-the-right-direction/"
        defined_for = StateCode.IL

        def formula(tax_unit, period, parameters):
            income = tax_unit("adjusted_gross_income", period)
            p = parameters(period).gov.contrib.states.il.child_tax_credit
            amount = p.amount
            children = tax_unit("ctc_qualifying_children", period)
            base_amount = amount * children
            married = tax_unit.family("is_married", period)
            phase_out = where(
                married,
                p.reduction.married.calc(income),
                p.reduction.single.calc(income),
            )
            return max_(base_amount - phase_out, 0)

    class reform(Reform):
        def apply(self):
            self.add_variable(il_child_tax_credit)

    return reform


def create_il_child_tax_credit_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_il_child_tax_credit()

    p = parameters(period).gov.contrib.states.il.child_tax_credit

    if p.amount > 0:
        return create_il_child_tax_credit()

    else:
        return None


il_child_tax_credit = create_il_child_tax_credit_reform(
    None, None, bypass=True
)
