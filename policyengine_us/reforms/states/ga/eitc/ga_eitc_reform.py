from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ga_eitc() -> Reform:
    class ga_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Georgia Earned Income Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.GA

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.states.ga.child_poverty_impact_dashboard.eitc
            federal_eitc = tax_unit("eitc", period)
            return federal_eitc * p.match

    class ga_refundable_credits(Variable):
        # NOTE: GA currently has no baseline refundable credits.
        # If GA adds refundable credits in baseline, this formula must be updated.
        value_type = float
        entity = TaxUnit
        label = "Georgia refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.GA

        def formula(tax_unit, period, parameters):
            return tax_unit("ga_eitc", period)

    class reform(Reform):
        def apply(self):
            self.update_variable(ga_eitc)
            self.update_variable(ga_refundable_credits)

    return reform


def create_ga_eitc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ga_eitc()

    p = parameters.gov.contrib.states.ga.child_poverty_impact_dashboard.eitc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        p_at_period = p(current_period)
        if p_at_period.in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ga_eitc()
    else:
        return None


ga_eitc = create_ga_eitc_reform(None, None, bypass=True)
