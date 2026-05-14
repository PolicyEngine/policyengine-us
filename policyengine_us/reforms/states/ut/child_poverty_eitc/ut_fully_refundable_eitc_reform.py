from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ut_fully_refundable_eitc() -> Reform:
    """
    Utah Fully Refundable EITC Reform

    Converts the Utah EITC from a nonrefundable credit to a fully refundable
    credit for ALL filers, including childless filers. This is different from
    the existing ut_refundable_eitc reform which only makes it refundable for
    families with young children.
    """

    class ut_fully_refundable_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah fully refundable EITC"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.UT

        def formula(tax_unit, period, parameters):
            return tax_unit("ut_eitc", period)

    class ut_non_refundable_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah nonrefundable EITC"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.UT

        def formula(tax_unit, period, parameters):
            # Reform makes EITC fully refundable, so nonrefundable portion is 0
            return 0

    class ut_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah non-refundable tax credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.UT

        def formula(tax_unit, period, parameters):
            # Use parameter-driven approach: get baseline non-refundable credits
            # then subtract ut_eitc (now refundable) and add back ut_non_refundable_eitc (0)
            baseline_non_refundable = add(
                tax_unit,
                period,
                "gov.states.ut.tax.income.credits.non_refundable",
            )
            # Remove ut_eitc from non-refundable (it's now handled separately)
            ut_eitc = tax_unit("ut_eitc", period)
            # Add back nonrefundable EITC (0 when reform is in effect)
            nonrefundable_eitc = tax_unit("ut_non_refundable_eitc", period)
            return baseline_non_refundable - ut_eitc + nonrefundable_eitc

    class ut_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.UT

        def formula(tax_unit, period, parameters):
            # Add the fully refundable EITC (positive when reform is in effect)
            return tax_unit("ut_fully_refundable_eitc", period)

    class reform(Reform):
        def apply(self):
            self.update_variable(ut_fully_refundable_eitc)
            self.update_variable(ut_non_refundable_eitc)
            self.update_variable(ut_non_refundable_credits)
            self.update_variable(ut_refundable_credits)

    return reform


def create_ut_fully_refundable_eitc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ut_fully_refundable_eitc()

    p = parameters.gov.contrib.states.ut.child_poverty_impact_dashboard.eitc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ut_fully_refundable_eitc()
    else:
        return None


ut_fully_refundable_eitc = create_ut_fully_refundable_eitc_reform(
    None, None, bypass=True
)
