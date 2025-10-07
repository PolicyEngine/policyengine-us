from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_aca_ptc_additional_bracket() -> Reform:
    class aca_ptc_phase_out_rate(Variable):
        """
        ACA Premium Tax Credit phase-out rate with linear bracket extension.

        This reform extends premium subsidies beyond the standard 400% FPL cliff
        using a linear formula. Above the transition threshold (typically 300% FPL),
        the contribution percentage increases linearly based on the increment rate
        (typically 4 percentage points per 100% FPL).

        The reform creates a more gradual phase-out of subsidies, reducing the
        cliff effect where households just above 400% FPL lose all subsidies.

        Related issue: https://github.com/PolicyEngine/policyengine-us/issues/6629
        """

        value_type = float
        entity = TaxUnit
        label = "ACA PTC phase-out rate with additional bracket (i.e., IRS Form 8962 'applicable figure')"
        unit = "/1"
        definition_period = YEAR
        reference = [
            "26 U.S. Code § 36B(b)(3)(A) - Refundable credit for coverage under a qualified health plan",
            "https://www.law.cornell.edu/uscode/text/26/36B#b_3_A",
        ]

        def formula(tax_unit, period, parameters):
            magi_frac = tax_unit("aca_magi_fraction", period)
            p = parameters(
                period
            ).gov.contrib.aca.ptc_additional_bracket.brackets
            return np.interp(magi_frac, p.thresholds, p.amounts)

    class reform(Reform):
        def apply(self):
            self.update_variable(aca_ptc_phase_out_rate)

    return reform


def create_aca_ptc_additional_bracket_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_aca_ptc_additional_bracket()

    p = parameters.gov.contrib.aca.ptc_additional_bracket
    current_period = period_(period)

    # Check if reform is active within a 5-year lookahead window
    # This allows the reform to be selected in the web app interface
    # even if it's scheduled to start in a future year
    reform_active = False
    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_aca_ptc_additional_bracket()
    else:
        return None


aca_ptc_additional_bracket = create_aca_ptc_additional_bracket_reform(
    None, None, bypass=True
)
