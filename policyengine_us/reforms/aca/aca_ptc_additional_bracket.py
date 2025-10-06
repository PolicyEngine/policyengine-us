from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_aca_ptc_additional_bracket() -> Reform:
    class aca_ptc_phase_out_rate(Variable):
        value_type = float
        entity = TaxUnit
        label = "ACA PTC phase-out rate with additional bracket (i.e., IRS Form 8962 'applicable figure')"
        unit = "/1"
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/36B#b_3_A"

        def formula(tax_unit, period, parameters):
            magi_frac = tax_unit("aca_magi_fraction", period)
            p = parameters(
                period
            ).gov.contrib.aca.ptc_additional_bracket.brackets
            return p.calc(magi_frac)

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

    reform_active = False
    current_period = period_(period)

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
