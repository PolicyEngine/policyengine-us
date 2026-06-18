from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    ordered_capped_state_non_refundable_credits,
)


def create_sc_fully_refundable_eitc() -> Reform:
    """
    South Carolina Fully Refundable EITC Reform

    Converts the South Carolina EITC from nonrefundable to fully refundable
    for ALL filers. SC's EITC is 125% of the federal EITC (subject to a
    per-filer cap — $200 from 2026) and is nonrefundable by default, i.e.
    applied only up to remaining state income tax liability. This reform pays
    the potential (uncapped-at-liability) credit as a refundable credit, so
    zero-liability filers receive it.

    Mirrors the corrected Utah/Missouri/Ohio refundability reforms
    (PolicyEngine/policyengine-us#8645, #8642, #8657): pay the ``*_potential``
    amount, rebuild the non-refundable bucket with the EITC filtered out of
    the ordered cap walk, and clear the inherited ``adds`` on the refundable
    aggregate before giving it a formula.

    Activated by
    ``gov.contrib.states.sc.child_poverty_impact_dashboard.eitc.in_effect``.

    Reference: SC Code Section 12-6-3632.
    """

    class sc_fully_refundable_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "South Carolina fully refundable EITC"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.SC

        def formula(tax_unit, period, parameters):
            # Pay the potential (uncapped-at-liability) SC EITC so the whole
            # credit is refundable; ``sc_eitc`` is capped at tax liability and
            # would zero out for the low-liability filers refundability is
            # meant to help. ``sc_eitc_potential`` still applies the statutory
            # per-filer cap (gov.states.sc.tax.income.credits.eitc.max).
            return tax_unit("sc_eitc_potential", period)

    class sc_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "South Carolina non-refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.SC

        def formula(tax_unit, period, parameters):
            # Mirror the baseline ordered-cap walk but drop sc_eitc from the
            # non-refundable bucket — it is paid as a refundable credit under
            # this reform. A raw ``sum - sc_eitc`` would overstate the total
            # whenever the bucket binds at liability, so re-run the ordered
            # walk over the filtered list instead.
            ordered_credits = parameters(
                period
            ).gov.states.sc.tax.income.credits.non_refundable
            filtered_credits = [
                credit for credit in list(ordered_credits) if credit != "sc_eitc"
            ]
            return ordered_capped_state_non_refundable_credits(
                tax_unit,
                period,
                filtered_credits,
                "sc_income_tax_before_non_refundable_credits",
            )

    class sc_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "South Carolina refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.SC
        # The baseline computes via ``adds``. We replace it with a formula, so
        # clear the inherited computation modes to avoid mixing ``formula``
        # with ``adds``/``subtracts`` (rejected by the core engine).
        adds = None
        subtracts = None

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.sc.tax.income.credits
            standard_credits = add(tax_unit, period, p.refundable)
            refundable_eitc = tax_unit("sc_fully_refundable_eitc", period)
            return standard_credits + refundable_eitc

    class reform(Reform):
        def apply(self):
            self.update_variable(sc_fully_refundable_eitc)
            self.update_variable(sc_non_refundable_credits)
            self.update_variable(sc_refundable_credits)

    return reform


def create_sc_fully_refundable_eitc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_sc_fully_refundable_eitc()

    p = parameters.gov.contrib.states.sc.child_poverty_impact_dashboard.eitc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_sc_fully_refundable_eitc()
    else:
        return None


sc_fully_refundable_eitc = create_sc_fully_refundable_eitc_reform(
    None, None, bypass=True
)
