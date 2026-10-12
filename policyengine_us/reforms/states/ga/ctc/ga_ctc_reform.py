from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    state_non_refundable_credit_limit,
)


def create_ga_ctc() -> Reform:
    class ga_refundable_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Georgia refundable child tax credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.GA

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ga.ctc
            # Potential is the full Georgia CTC worksheet amount before the
            # nonrefundable liability limit.
            potential = tax_unit("ga_ctc_potential", period)
            ordered_credits = parameters(
                period
            ).gov.states.ga.tax.income.credits.non_refundable
            credit_limit = state_non_refundable_credit_limit(
                tax_unit,
                period,
                ordered_credits,
                "ga_income_tax_before_non_refundable_credits",
                "ga_ctc",
            )
            non_refundable = min_(potential, credit_limit)
            unused_credit = max_(potential - non_refundable, 0)
            # Cap the refund at amount per eligible child (same child count as
            # ga_ctc_potential: qualifying children under the age threshold).
            baseline = parameters(period).gov.states.ga.tax.income.credits.ctc
            person = tax_unit.members
            age = person("age", period)
            ctc_eligible_child = person("ctc_qualifying_child", period)
            ga_child_age_eligible = age < baseline.age_threshold
            eligible_children = tax_unit.sum(ctc_eligible_child & ga_child_age_eligible)
            refund_limit = p.refundable.amount * eligible_children
            refundable_credit = min_(unused_credit, refund_limit)
            # Only pay the refund in periods where the reform is in effect. The
            # reform is installed for the whole simulation whenever it activates
            # in any of the next five years (see create_ga_ctc_reform), so this
            # per-period gate prevents a refund leaking into pre-activation years.
            return where(p.refundable.in_effect, refundable_credit, 0)

    class ga_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Georgia refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.GA
        adds = ["ga_refundable_ctc"]

    class reform(Reform):
        def apply(self):
            self.update_variable(ga_refundable_ctc)
            self.update_variable(ga_refundable_credits)

    return reform


def create_ga_ctc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ga_ctc()

    p = parameters.gov.contrib.states.ga.ctc

    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        if p(current_period).refundable.in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ga_ctc()
    else:
        return None


ga_ctc_reform = create_ga_ctc_reform(None, None, bypass=True)
