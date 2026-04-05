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
            return tax_unit("mo_wftc", period)

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
            # Include the nonrefundable WFTC (0 when reform is in effect)
            return tax_unit("mo_non_refundable_wftc", period)

    class mo_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Missouri refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MO

        def formula(tax_unit, period, parameters):
            # Standard refundable credits
            other_refundable = add(
                tax_unit,
                period,
                "gov.states.mo.tax.income.credits.refundable",
            )
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
