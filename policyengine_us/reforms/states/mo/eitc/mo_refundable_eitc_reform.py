from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_mo_refundable_eitc() -> Reform:
    """
    Missouri Refundable EITC Reform

    Converts the Missouri Working Families Tax Credit (WFTC) from a
    nonrefundable credit to a refundable credit. By default, MO WFTC
    is nonrefundable starting in 2023.
    """

    class mo_refundable_wftc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Missouri refundable Working Families Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MO

        def formula(tax_unit, period, parameters):
            # Use the potential (uncapped) WFTC so the full credit is paid as
            # a refund; `mo_wftc` is capped at tax liability and would zero out
            # the credit for the low-liability filers refundability is meant
            # to help.
            return tax_unit("mo_wftc_potential", period)

    class mo_non_refundable_wftc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Missouri nonrefundable Working Families Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MO

        def formula(tax_unit, period, parameters):
            # Reform makes WFTC fully refundable, so nonrefundable portion is 0
            return 0

    class mo_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Missouri non-refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MO

        def formula(tax_unit, period, parameters):
            # Today `gov.states.mo.tax.income.credits.non_refundable` is
            # just `[mo_wftc]`, so returning the (zeroed) reform replacement
            # is equivalent to the baseline. If Missouri later adds a second
            # nonrefundable credit, this formula would silently drop it —
            # at that point switch to summing the full nonrefundable list
            # with `mo_wftc` filtered out, mirroring the UT/OH fix pattern.
            return tax_unit("mo_non_refundable_wftc", period)

    class mo_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Missouri refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MO
        # The baseline variable computes via `adds`. We replace it with a
        # formula, so clear the inherited computation modes to avoid mixing
        # `formula` with `adds`/`subtracts` (rejected by the core engine).
        adds = None
        subtracts = None

        def formula(tax_unit, period, parameters):
            # Standard refundable credits, resolved to the list of variable
            # names before passing to `add` (which iterates variable names).
            refundable_credits = parameters(
                period
            ).gov.states.mo.tax.income.credits.refundable
            other_refundable = add(tax_unit, period, refundable_credits)
            # Add refundable WFTC (positive when reform is in effect)
            refundable_wftc = tax_unit("mo_refundable_wftc", period)
            return other_refundable + refundable_wftc

    class reform(Reform):
        def apply(self):
            self.update_variable(mo_refundable_wftc)
            self.update_variable(mo_non_refundable_wftc)
            self.update_variable(mo_non_refundable_credits)
            self.update_variable(mo_refundable_credits)

    return reform


def create_mo_refundable_eitc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_mo_refundable_eitc()

    p = parameters.gov.contrib.states.mo.child_poverty_impact_dashboard.eitc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_mo_refundable_eitc()
    else:
        return None


mo_refundable_eitc = create_mo_refundable_eitc_reform(None, None, bypass=True)
