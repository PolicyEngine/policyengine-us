from policyengine_us.model_api import *
from policyengine_core.periods import instant
from policyengine_core.periods import period as period_
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    state_non_refundable_credit_limit,
)


def create_id_ctc() -> Reform:
    class id_refundable_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Idaho refundable child tax credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.ID

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.id.ctc
            # Potential is the revived (nonrefundable) Idaho CTC worksheet
            # amount, ctc_qualifying_children * amount.
            potential = tax_unit("id_ctc", period)
            ordered_credits = parameters(
                period
            ).gov.states.id.tax.income.credits.non_refundable
            credit_limit = state_non_refundable_credit_limit(
                tax_unit,
                period,
                ordered_credits,
                "id_income_tax_before_non_refundable_credits",
                "id_ctc",
            )
            non_refundable = min_(potential, credit_limit)
            unused_credit = max_(potential - non_refundable, 0)
            eligible_children = tax_unit("ctc_qualifying_children", period)
            refund_limit = p.refundable.amount * eligible_children
            refundable_credit = min_(unused_credit, refund_limit)
            # Only pay the refundable portion when the refundable option is on;
            # otherwise the revival stays purely nonrefundable.
            return where(p.refundable.in_effect, refundable_credit, 0)

    def modify_parameters(parameters):
        # Revive id_ctc in the ordered nonrefundable list (it was dropped as of
        # 2026), so the baseline credit applies against liability again.
        non_refundable = parameters.gov.states.id.tax.income.credits.non_refundable
        current_non_refundable = non_refundable(instant("2026-01-01"))
        if "id_ctc" not in current_non_refundable:
            non_refundable.update(
                start=instant("2026-01-01"),
                stop=instant("2100-12-31"),
                value=list(current_non_refundable) + ["id_ctc"],
            )
        # Register the refundable top-up in the refundable list.
        refundable = parameters.gov.states.id.tax.income.credits.refundable
        current_refundable = refundable(instant("2026-01-01"))
        if "id_refundable_ctc" not in current_refundable:
            refundable.update(
                start=instant("2026-01-01"),
                stop=instant("2100-12-31"),
                value=list(current_refundable) + ["id_refundable_ctc"],
            )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(id_refundable_ctc)
            self.modify_parameters(modify_parameters)

    return reform


def create_id_ctc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_id_ctc()

    p = parameters.gov.contrib.states.id.ctc

    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        node = p(current_period)
        if node.in_effect or node.refundable.in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_id_ctc()
    else:
        return None


id_ctc_reform = create_id_ctc_reform(None, None, bypass=True)
