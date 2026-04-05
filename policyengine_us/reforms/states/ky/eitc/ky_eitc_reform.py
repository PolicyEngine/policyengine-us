from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ky_eitc() -> Reform:
    class ky_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Kentucky Earned Income Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.KY

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.states.ky.child_poverty_impact_dashboard.eitc
            federal_eitc = tax_unit("eitc", period)
            return federal_eitc * p.match

    class ky_refundable_credits(Variable):
        # NOTE: KY currently has no baseline refundable credits.
        # If KY adds refundable credits in baseline, this formula must be updated.
        value_type = float
        entity = TaxUnit
        label = "Kentucky refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.KY

        def formula(tax_unit, period, parameters):
            return tax_unit("ky_eitc", period)

    class reform(Reform):
        def apply(self):
            self.update_variable(ky_eitc)
            self.update_variable(ky_refundable_credits)

    return reform


def create_ky_eitc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ky_eitc()

    p = parameters.gov.contrib.states.ky.child_poverty_impact_dashboard.eitc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        p_at_period = p(current_period)
        if p_at_period.in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ky_eitc()
    else:
        return None


ky_eitc = create_ky_eitc_reform(None, None, bypass=True)
