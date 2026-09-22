from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    state_non_refundable_credit_limit,
)


def create_az_dependent_credit() -> Reform:
    class az_dependent_tax_credit_potential(Variable):
        value_type = float
        entity = TaxUnit
        label = "Arizona dependent tax credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.AZ

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            p_base = parameters(
                period
            ).gov.states.az.tax.income.credits.dependent_credit
            p = parameters(period).gov.contrib.states.az.dependent_credit
            dependent = person("is_tax_unit_dependent", period)
            age = person("age", period)
            if p.age_limit.in_effect:
                eligible = dependent & (age < p.age_limit.threshold)
            else:
                eligible = dependent
            per_dependent = where(p.amount < 0, p_base.amount.calc(age), p.amount)
            amount = tax_unit.sum(per_dependent * eligible)
            income = tax_unit("adjusted_gross_income", period)
            filing_status = tax_unit("filing_status", period)
            reduction_start = p_base.reduction.start[filing_status]
            excess = max_(income - reduction_start, 0)
            increments = np.ceil(excess / p_base.reduction.increment)
            reduction_percentage = min_(increments * p_base.reduction.percentage, 1)
            return amount * (1 - reduction_percentage)

    class reform(Reform):
        def apply(self):
            self.update_variable(az_dependent_tax_credit_potential)

    return reform


def create_az_dependent_credit_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_az_dependent_credit()

    p = parameters.gov.contrib.states.az.dependent_credit

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_az_dependent_credit()
    else:
        return None


az_dependent_credit_reform = create_az_dependent_credit_reform_fn(
    None, None, bypass=True
)


def create_az_refundable_dependent_credit() -> Reform:
    class az_refundable_dependent_tax_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Arizona refundable dependent tax credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.AZ

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.az.dependent_credit
            # Potential is the full dependent credit before the
            # nonrefundable liability limit. When the dependent-credit
            # contrib (amount/age levers) is also active it overrides the
            # potential, so the two reforms compose.
            potential = tax_unit("az_dependent_tax_credit_potential", period)
            # This refund inherits the baseline
            # gov.states.az.tax.income.credits.non_refundable ordering: the
            # stranded (unused) dependent credit is whatever this ordered list
            # leaves after higher-priority credits consume liability. That
            # baseline list currently applies the charitable credit before the
            # dependent/family credits, contrary to AZ Forms 140/301, which
            # apply the dependent and family credits first. In baseline the
            # ordering is invisible (same total, same az_income_tax), but with
            # this refund on it can strand the dependent credit and pay a
            # refund the form would not. Reordering the baseline list to
            # dependent, family, then charitable is tracked as a separate
            # follow-up issue rather than fixed in this reform (see
            # https://github.com/PolicyEngine/policyengine-us/issues/9559).
            ordered_credits = parameters(
                period
            ).gov.states.az.tax.income.credits.non_refundable
            credit_limit = state_non_refundable_credit_limit(
                tax_unit,
                period,
                ordered_credits,
                "az_income_tax_before_non_refundable_credits",
                "az_dependent_tax_credit",
            )
            non_refundable = min_(potential, credit_limit)
            unused_credit = max_(potential - non_refundable, 0)
            # Only pay the refund in periods where the reform is in effect.
            # The reform is installed for the whole simulation whenever it
            # activates in any of the next five years (see
            # create_az_refundable_dependent_credit_reform_fn), so this
            # per-period gate prevents a refund leaking into
            # pre-activation years.
            return where(p.refundable.in_effect, unused_credit, 0)

    def modify_parameters(parameters):
        node = parameters.gov.states.az.tax.income.credits.refundable
        current = node("2024-01-01")
        # modify_parameters can run more than once per build; guard the
        # append so the refund is registered exactly once.
        if "az_refundable_dependent_tax_credit" not in current:
            node.update(
                start=instant("2024-01-01"),
                stop=instant("2100-12-31"),
                value=list(current) + ["az_refundable_dependent_tax_credit"],
            )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(az_refundable_dependent_tax_credit)
            self.modify_parameters(modify_parameters)

    return reform


def create_az_refundable_dependent_credit_reform_fn(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_az_refundable_dependent_credit()

    p = parameters.gov.contrib.states.az.dependent_credit

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).refundable.in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_az_refundable_dependent_credit()
    else:
        return None


az_refundable_dependent_credit_reform = create_az_refundable_dependent_credit_reform_fn(
    None, None, bypass=True
)
